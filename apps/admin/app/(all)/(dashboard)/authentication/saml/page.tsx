/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import useSWR from "swr";
import { PageWrapper } from "@/components/common/page-wrapper";
import { Skeleton } from "@/components/common/skeleton";
import { InstanceExtConfigForm } from "@/components/authentication/ext-config-form";
import { useInstance } from "@/hooks/store";
import type { Route } from "./+types/page";

const Page = observer(function Page(_props: Route.ComponentProps) {
  const { fetchInstanceConfigurations, formattedConfig } = useInstance();
  useSWR("INSTANCE_CONFIGURATIONS", () => fetchInstanceConfigurations());
  return (
    <PageWrapper header={{ title: "SAML", description: "SAML 2.0 single sign-on." }}>
      {formattedConfig ? (
        <InstanceExtConfigForm
          config={formattedConfig}
          title="SAML"
          enableKey="ENABLE_SAML_SYNC"
          callbackPath="/auth/saml/callback/"
          fields={[
            { key: "SAML_IDP_SSO_URL", type: "text", label: "IdP SSO URL", required: true },
            { key: "SAML_IDP_ENTITY_ID", type: "text", label: "IdP entity ID", required: true },
            { key: "SAML_SP_ENTITY_ID", type: "text", label: "SP entity ID" },
            { key: "SAML_IDP_X509", type: "password", label: "IdP X.509 certificate" },
          ]}
        />
      ) : (
        <Skeleton className="space-y-8">
          <Skeleton.Item height="50px" />
        </Skeleton>
      )}
    </PageWrapper>
  );
});

export const meta: Route.MetaFunction = () => [{ title: "SAML Authentication - God Mode" }];
export default Page;
