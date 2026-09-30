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
    <PageWrapper header={{ title: "OIDC", description: "OpenID Connect single sign-on." }}>
      {formattedConfig ? (
        <InstanceExtConfigForm
          config={formattedConfig}
          title="OIDC"
          enableKey="ENABLE_OIDC_SYNC"
          callbackPath="/auth/oidc/callback/"
          fields={[
            { key: "OIDC_ISSUER", type: "text", label: "Issuer URL", required: true },
            { key: "OIDC_CLIENT_ID", type: "text", label: "Client ID", required: true },
            { key: "OIDC_CLIENT_SECRET", type: "password", label: "Client secret", required: true },
            { key: "OIDC_SCOPES", type: "text", label: "Scopes" },
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

export const meta: Route.MetaFunction = () => [{ title: "OIDC Authentication - God Mode" }];
export default Page;
