# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import base64
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

from plane.authentication.adapter.error import (
    AUTHENTICATION_ERROR_CODES,
    AuthenticationException,
)
from plane.authentication.adapter.oauth import OauthAdapter
from plane.license.utils.instance_value import get_configuration_value

NS = {
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
}


class SAMLProvider(OauthAdapter):
    provider = "saml"
    scope = "saml"
    token_url = ""
    userinfo_url = ""

    def __init__(self, request, code=None, state=None, callback=None, saml_response=None):
        (
            SAML_IDP_SSO_URL,
            SAML_IDP_ENTITY_ID,
            SAML_SP_ENTITY_ID,
            SAML_IDP_X509,
        ) = get_configuration_value(
            [
                {"key": "SAML_IDP_SSO_URL", "default": os.environ.get("SAML_IDP_SSO_URL")},
                {"key": "SAML_IDP_ENTITY_ID", "default": os.environ.get("SAML_IDP_ENTITY_ID")},
                {"key": "SAML_SP_ENTITY_ID", "default": os.environ.get("SAML_SP_ENTITY_ID")},
                {"key": "SAML_IDP_X509", "default": os.environ.get("SAML_IDP_X509")},
            ]
        )

        if not (SAML_IDP_SSO_URL and SAML_IDP_ENTITY_ID):
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_NOT_CONFIGURED"],
                error_message="SAML_NOT_CONFIGURED",
            )

        self.idp_sso_url = SAML_IDP_SSO_URL
        self.idp_entity_id = SAML_IDP_ENTITY_ID
        self.sp_entity_id = SAML_SP_ENTITY_ID or f"{'https' if request.is_secure() else 'http'}://{request.get_host()}"
        self.idp_x509 = SAML_IDP_X509
        self.saml_response = saml_response
        redirect_uri = f"""{"https" if request.is_secure() else "http"}://{request.get_host()}/auth/saml/callback/"""
        request_id = f"_{uuid.uuid4().hex}"
        issue_instant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        authn_request = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            f'<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" '
            f'xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="{request_id}" Version="2.0" '
            f'IssueInstant="{issue_instant}" Destination="{SAML_IDP_SSO_URL}" '
            f'AssertionConsumerServiceURL="{redirect_uri}" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">'
            f"<saml:Issuer>{self.sp_entity_id}</saml:Issuer>"
            "<samlp:NameIDPolicy Format=\"urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress\" AllowCreate=\"true\"/>"
            "</samlp:AuthnRequest>"
        )
        saml_request = base64.b64encode(authn_request.encode("utf-8")).decode("ascii")
        params = {"SAMLRequest": saml_request}
        if state:
            params["RelayState"] = state
        auth_url = f"{SAML_IDP_SSO_URL}?{urlencode(params)}"

        super().__init__(
            request,
            self.provider,
            self.sp_entity_id,
            self.scope,
            redirect_uri,
            auth_url,
            self.token_url,
            self.userinfo_url,
            None,
            code,
            callback=callback,
        )

    def authenticate(self):
        self.set_token_data()
        self.set_user_data()
        return self.complete_login_or_signup()

    def set_token_data(self):
        super().set_token_data(
            {
                "access_token": "",
                "refresh_token": None,
                "access_token_expired_at": None,
                "refresh_token_expired_at": None,
                "id_token": self.saml_response or "",
            }
        )

    def _parse_assertion(self, xml_text):
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )

        name_id = root.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}NameID")
        email = name_id.text.strip() if name_id is not None and name_id.text else None
        first_name = ""
        last_name = ""
        provider_id = email
        for attr in root.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"):
            name = (attr.get("Name") or "").lower()
            values = [
                v.text
                for v in attr.findall("{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                if v.text
            ]
            if not values:
                continue
            if "email" in name and not email:
                email = values[0].strip()
            elif name.endswith("givenname") or "first_name" in name:
                first_name = values[0]
            elif name.endswith("surname") or "last_name" in name:
                last_name = values[0]
            elif "nameid" in name or name.endswith("uid"):
                provider_id = values[0]
        if not email:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )
        return email, first_name, last_name, provider_id or email

    def set_user_data(self):
        if not self.saml_response:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )
        try:
            xml_text = base64.b64decode(self.saml_response).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )
        email, first_name, last_name, provider_id = self._parse_assertion(xml_text)
        super().set_user_data(
            {
                "email": email,
                "user": {
                    "avatar": "",
                    "first_name": first_name,
                    "last_name": last_name,
                    "provider_id": provider_id,
                    "is_password_autoset": True,
                },
            }
        )
