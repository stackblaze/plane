/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useSearchParams } from "next/navigation";
import { API_BASE_URL } from "@plane/constants";
import type { TOAuthConfigs, TOAuthOption } from "@plane/types";
import { useInstance } from "@/hooks/store/use-instance";

export const useExtendedOAuthConfig = (oauthActionText: string): TOAuthConfigs => {
  const searchParams = useSearchParams();
  const next_path = searchParams.get("next_path");
  const { config } = useInstance();
  const suffix = next_path ? `?next_path=${next_path}` : "";
  const oAuthOptions: TOAuthOption[] = [
    {
      id: "oidc",
      text: `${oauthActionText} with OIDC`,
      icon: <span className="text-11 font-medium">OIDC</span>,
      onClick: () => window.location.assign(`${API_BASE_URL}/auth/oidc/${suffix}`),
      enabled: config?.is_oidc_enabled,
    },
    {
      id: "saml",
      text: `${oauthActionText} with SAML`,
      icon: <span className="text-11 font-medium">SAML</span>,
      onClick: () => window.location.assign(`${API_BASE_URL}/auth/saml/${suffix}`),
      enabled: config?.is_saml_enabled,
    },
    {
      id: "ldap",
      text: `${oauthActionText} with LDAP`,
      icon: <span className="text-11 font-medium">LDAP</span>,
      onClick: () => {
        const email = (document.querySelector('input[name="email"]') as HTMLInputElement | null)?.value;
        const password = (document.querySelector('input[name="password"]') as HTMLInputElement | null)?.value;
        void fetch(`${API_BASE_URL}/auth/get-csrf-token/`, { credentials: "include" })
          .then((response) => response.json())
          .then((data) => {
            const form = document.createElement("form");
            form.method = "POST";
            form.action = `${API_BASE_URL}/auth/ldap/`;
            const add = (name: string, value: string) => {
              const input = document.createElement("input");
              input.type = "hidden";
              input.name = name;
              input.value = value;
              form.appendChild(input);
            };
            add("csrfmiddlewaretoken", data?.csrf_token || "");
            add("email", email || "");
            add("password", password || "");
            if (next_path) add("next_path", next_path);
            document.body.appendChild(form);
            form.submit();
          });
      },
      enabled: config?.is_ldap_enabled,
    },
  ];
  return {
    isOAuthEnabled: Boolean(config?.is_oidc_enabled || config?.is_saml_enabled || config?.is_ldap_enabled),
    oAuthOptions,
  };
};
