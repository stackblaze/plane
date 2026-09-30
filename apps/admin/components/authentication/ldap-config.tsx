/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import Link from "next/link";
import { SettingsOutline } from "@makeplane/propel/icons";
import { AnchorButton } from "@makeplane/propel/components/anchor-button";
import { Button } from "@makeplane/propel/components/button";
import { Switch } from "@makeplane/propel/components/switch";
import type { TInstanceAuthenticationMethodKeys } from "@plane/types";
import { useInstance } from "@/hooks/store";

type Props = {
  disabled: boolean;
  updateConfig: (key: TInstanceAuthenticationMethodKeys, value: string) => void;
};

export const LDAPConfiguration = observer(function LDAPConfiguration(props: Props) {
  const { disabled, updateConfig } = props;
  const { formattedConfig } = useInstance();
  const enabled = formattedConfig?.IS_LDAP_ENABLED ?? "";
  const configured = !!formattedConfig?.LDAP_SERVER_URL && !!formattedConfig?.LDAP_USER_SEARCH_BASE;

  return configured ? (
    <div className="flex items-center gap-4">
      <AnchorButton variant="primary" size="sm" render={<Link href="/authentication/ldap" />} label="Edit" />
      <Switch
        checked={Boolean(parseInt(enabled))}
        onCheckedChange={() => updateConfig("IS_LDAP_ENABLED", Boolean(parseInt(enabled)) ? "0" : "1")}
        size="sm"
        aria-label="Enable LDAP"
        disabled={disabled}
      />
    </div>
  ) : (
    <Button
      variant="secondary"
      size="sm"
      stretch="auto"
      nativeButton={false}
      render={<Link href="/authentication/ldap" />}
      icon={<SettingsOutline className="h-4 w-4 p-0.5 text-tertiary" />}
      label="Configure"
    />
  );
});
