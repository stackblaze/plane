/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export type TExtendedLoginMediums = "oidc" | "saml" | "ldap";

export type TExtendedInstanceAuthenticationModeKeys = "oidc" | "saml" | "ldap";

export type TInstanceOIDCAuthenticationConfigurationKeys =
  | "OIDC_ISSUER"
  | "OIDC_CLIENT_ID"
  | "OIDC_CLIENT_SECRET"
  | "OIDC_SCOPES"
  | "ENABLE_OIDC_SYNC";

export type TInstanceSAMLAuthenticationConfigurationKeys =
  | "SAML_IDP_SSO_URL"
  | "SAML_IDP_ENTITY_ID"
  | "SAML_SP_ENTITY_ID"
  | "SAML_IDP_X509"
  | "ENABLE_SAML_SYNC";

export type TInstanceLDAPAuthenticationConfigurationKeys =
  | "LDAP_SERVER_URL"
  | "LDAP_BIND_DN"
  | "LDAP_BIND_PASSWORD"
  | "LDAP_USER_SEARCH_BASE"
  | "LDAP_USER_FILTER"
  | "LDAP_EMAIL_ATTR"
  | "LDAP_GROUP_SEARCH_BASE"
  | "LDAP_GROUP_FILTER"
  | "LDAP_GROUP_ROLE_MAP"
  | "ENABLE_LDAP_SYNC";

