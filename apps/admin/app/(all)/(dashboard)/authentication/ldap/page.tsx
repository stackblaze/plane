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
    <PageWrapper header={{ title: "LDAP", description: "Directory bind and group sync." }}>
      {formattedConfig ? (
        <InstanceExtConfigForm
          config={formattedConfig}
          title="LDAP"
          enableKey="ENABLE_LDAP_SYNC"
          callbackPath="/auth/ldap/"
          fields={[
            { key: "LDAP_SERVER_URL", type: "text", label: "Server URL", required: true },
            { key: "LDAP_BIND_DN", type: "text", label: "Bind DN" },
            { key: "LDAP_BIND_PASSWORD", type: "password", label: "Bind password" },
            { key: "LDAP_USER_SEARCH_BASE", type: "text", label: "User search base", required: true },
            { key: "LDAP_USER_FILTER", type: "text", label: "User filter" },
            { key: "LDAP_EMAIL_ATTR", type: "text", label: "Email attribute" },
            { key: "LDAP_GROUP_SEARCH_BASE", type: "text", label: "Group search base" },
            { key: "LDAP_GROUP_FILTER", type: "text", label: "Group filter" },
            { key: "LDAP_GROUP_ROLE_MAP", type: "text", label: "Group to role map (JSON)" },
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

export const meta: Route.MetaFunction = () => [{ title: "LDAP Authentication - God Mode" }];
export default Page;
