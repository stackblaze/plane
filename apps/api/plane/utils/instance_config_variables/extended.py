# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import os

oidc_config_variables = [
    {
        "key": "IS_OIDC_ENABLED",
        "value": os.environ.get("IS_OIDC_ENABLED", "0"),
        "category": "OIDC",
        "is_encrypted": False,
    },
    {
        "key": "OIDC_ISSUER",
        "value": os.environ.get("OIDC_ISSUER", ""),
        "category": "OIDC",
        "is_encrypted": False,
    },
    {
        "key": "OIDC_CLIENT_ID",
        "value": os.environ.get("OIDC_CLIENT_ID", ""),
        "category": "OIDC",
        "is_encrypted": False,
    },
    {
        "key": "OIDC_CLIENT_SECRET",
        "value": os.environ.get("OIDC_CLIENT_SECRET", ""),
        "category": "OIDC",
        "is_encrypted": True,
    },
    {
        "key": "OIDC_SCOPES",
        "value": os.environ.get("OIDC_SCOPES", "openid email profile"),
        "category": "OIDC",
        "is_encrypted": False,
    },
    {
        "key": "ENABLE_OIDC_SYNC",
        "value": os.environ.get("ENABLE_OIDC_SYNC", "0"),
        "category": "OIDC",
        "is_encrypted": False,
    },
]

saml_config_variables = [
    {
        "key": "IS_SAML_ENABLED",
        "value": os.environ.get("IS_SAML_ENABLED", "0"),
        "category": "SAML",
        "is_encrypted": False,
    },
    {
        "key": "SAML_IDP_SSO_URL",
        "value": os.environ.get("SAML_IDP_SSO_URL", ""),
        "category": "SAML",
        "is_encrypted": False,
    },
    {
        "key": "SAML_IDP_ENTITY_ID",
        "value": os.environ.get("SAML_IDP_ENTITY_ID", ""),
        "category": "SAML",
        "is_encrypted": False,
    },
    {
        "key": "SAML_SP_ENTITY_ID",
        "value": os.environ.get("SAML_SP_ENTITY_ID", ""),
        "category": "SAML",
        "is_encrypted": False,
    },
    {
        "key": "SAML_IDP_X509",
        "value": os.environ.get("SAML_IDP_X509", ""),
        "category": "SAML",
        "is_encrypted": True,
    },
    {
        "key": "ENABLE_SAML_SYNC",
        "value": os.environ.get("ENABLE_SAML_SYNC", "0"),
        "category": "SAML",
        "is_encrypted": False,
    },
]

ldap_config_variables = [
    {
        "key": "IS_LDAP_ENABLED",
        "value": os.environ.get("IS_LDAP_ENABLED", "0"),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_SERVER_URL",
        "value": os.environ.get("LDAP_SERVER_URL", ""),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_BIND_DN",
        "value": os.environ.get("LDAP_BIND_DN", ""),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_BIND_PASSWORD",
        "value": os.environ.get("LDAP_BIND_PASSWORD", ""),
        "category": "LDAP",
        "is_encrypted": True,
    },
    {
        "key": "LDAP_USER_SEARCH_BASE",
        "value": os.environ.get("LDAP_USER_SEARCH_BASE", ""),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_USER_FILTER",
        "value": os.environ.get("LDAP_USER_FILTER", "(mail={email})"),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_EMAIL_ATTR",
        "value": os.environ.get("LDAP_EMAIL_ATTR", "mail"),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_GROUP_SEARCH_BASE",
        "value": os.environ.get("LDAP_GROUP_SEARCH_BASE", ""),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_GROUP_FILTER",
        "value": os.environ.get("LDAP_GROUP_FILTER", "(member={dn})"),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "LDAP_GROUP_ROLE_MAP",
        "value": os.environ.get("LDAP_GROUP_ROLE_MAP", "{}"),
        "category": "LDAP",
        "is_encrypted": False,
    },
    {
        "key": "ENABLE_LDAP_SYNC",
        "value": os.environ.get("ENABLE_LDAP_SYNC", "0"),
        "category": "LDAP",
        "is_encrypted": False,
    },
]

extended_config_variables = [
    *oidc_config_variables,
    *saml_config_variables,
    *ldap_config_variables,
]
