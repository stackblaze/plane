# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import json
import os

from plane.authentication.adapter.credential import CredentialAdapter
from plane.authentication.adapter.error import (
    AUTHENTICATION_ERROR_CODES,
    AuthenticationException,
)
from plane.db.models import User, Workspace, WorkspaceMember
from plane.license.utils.instance_value import get_configuration_value


class LDAPProvider(CredentialAdapter):
    provider = "ldap"

    def __init__(self, request, key=None, code=None, callback=None):
        super().__init__(request=request, provider=self.provider, callback=callback)
        self.key = key
        self.code = code
        (
            IS_LDAP_ENABLED,
            self.server_url,
            self.bind_dn,
            self.bind_password,
            self.user_search_base,
            self.user_filter,
            self.email_attr,
            self.group_search_base,
            self.group_filter,
            self.group_role_map,
        ) = get_configuration_value(
            [
                {"key": "IS_LDAP_ENABLED", "default": os.environ.get("IS_LDAP_ENABLED", "0")},
                {"key": "LDAP_SERVER_URL", "default": os.environ.get("LDAP_SERVER_URL")},
                {"key": "LDAP_BIND_DN", "default": os.environ.get("LDAP_BIND_DN")},
                {"key": "LDAP_BIND_PASSWORD", "default": os.environ.get("LDAP_BIND_PASSWORD")},
                {"key": "LDAP_USER_SEARCH_BASE", "default": os.environ.get("LDAP_USER_SEARCH_BASE")},
                {
                    "key": "LDAP_USER_FILTER",
                    "default": os.environ.get("LDAP_USER_FILTER", "(mail={email})"),
                },
                {"key": "LDAP_EMAIL_ATTR", "default": os.environ.get("LDAP_EMAIL_ATTR", "mail")},
                {
                    "key": "LDAP_GROUP_SEARCH_BASE",
                    "default": os.environ.get("LDAP_GROUP_SEARCH_BASE"),
                },
                {
                    "key": "LDAP_GROUP_FILTER",
                    "default": os.environ.get("LDAP_GROUP_FILTER", "(member={dn})"),
                },
                {"key": "LDAP_GROUP_ROLE_MAP", "default": os.environ.get("LDAP_GROUP_ROLE_MAP", "{}")},
            ]
        )

        if IS_LDAP_ENABLED == "0" or not (self.server_url and self.user_search_base):
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["LDAP_NOT_CONFIGURED"],
                error_message="LDAP_NOT_CONFIGURED",
            )

    def _connect(self):
        try:
            from ldap3 import ALL, Connection, Server
        except ImportError:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["LDAP_NOT_CONFIGURED"],
                error_message="LDAP_NOT_CONFIGURED",
            )
        server = Server(self.server_url, get_info=ALL)
        if self.bind_dn:
            conn = Connection(server, user=self.bind_dn, password=self.bind_password or "", auto_bind=True)
        else:
            conn = Connection(server, auto_bind=True)
        return conn

    def _search_user(self, conn):
        from ldap3 import SUBTREE

        filt = (self.user_filter or "(mail={email})").format(email=self.key, username=self.key)
        conn.search(self.user_search_base, filt, SUBTREE, attributes=[self.email_attr, "givenName", "sn", "cn"])
        if not conn.entries:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["USER_DOES_NOT_EXIST"],
                error_message="USER_DOES_NOT_EXIST",
                payload={"email": self.key},
            )
        return conn.entries[0]

    def _bind_user(self, user_dn):
        try:
            from ldap3 import Connection, Server
        except ImportError:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["LDAP_NOT_CONFIGURED"],
                error_message="LDAP_NOT_CONFIGURED",
            )
        try:
            server = Server(self.server_url)
            conn = Connection(server, user=user_dn, password=self.code, auto_bind=True)
            conn.unbind()
        except Exception:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["AUTHENTICATION_FAILED_SIGN_IN"],
                error_message="AUTHENTICATION_FAILED_SIGN_IN",
                payload={"email": self.key},
            )

    def _sync_groups(self, conn, user_dn, email):
        if not self.group_search_base or not self.check_sync_enabled():
            return
        try:
            role_map = json.loads(self.group_role_map or "{}")
        except json.JSONDecodeError:
            role_map = {}
        if not role_map:
            return
        from ldap3 import SUBTREE

        filt = (self.group_filter or "(member={dn})").format(dn=user_dn, email=email)
        conn.search(self.group_search_base, filt, SUBTREE, attributes=["cn"])
        user = User.objects.filter(email=email).first()
        if not user:
            return
        for entry in conn.entries:
            cn = str(entry.cn) if hasattr(entry, "cn") else ""
            role = role_map.get(cn)
            if role is None:
                continue
            try:
                role = int(role)
            except (TypeError, ValueError):
                continue
            for workspace in Workspace.objects.all():
                member, created = WorkspaceMember.objects.get_or_create(
                    workspace=workspace,
                    member=user,
                    defaults={"role": role, "is_active": True},
                )
                if not created and member.role != role:
                    member.role = role
                    member.save(update_fields=["role"])

    def set_user_data(self):
        if not self.key or not self.code:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["REQUIRED_EMAIL_PASSWORD_SIGN_IN"],
                error_message="REQUIRED_EMAIL_PASSWORD_SIGN_IN",
            )
        email = self.sanitize_email(self.key)
        try:
            conn = self._connect()
            entry = self._search_user(conn)
            user_dn = entry.entry_dn
            self._bind_user(user_dn)
            mail_values = entry[self.email_attr].values if self.email_attr in entry else [email]
            resolved_email = self.sanitize_email(mail_values[0] if mail_values else email)
            first_name = str(entry.givenName) if hasattr(entry, "givenName") and entry.givenName else ""
            last_name = str(entry.sn) if hasattr(entry, "sn") and entry.sn else ""
            self._sync_groups(conn, user_dn, resolved_email)
            conn.unbind()
        except AuthenticationException:
            raise
        except Exception:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["LDAP_PROVIDER_ERROR"],
                error_message="LDAP_PROVIDER_ERROR",
            )
        super().set_user_data(
            {
                "email": resolved_email,
                "user": {
                    "avatar": "",
                    "first_name": first_name,
                    "last_name": last_name,
                    "provider_id": user_dn,
                    "is_password_autoset": True,
                },
            }
        )
