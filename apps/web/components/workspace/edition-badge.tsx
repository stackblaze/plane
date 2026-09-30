/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useTranslation } from "@plane/i18n";
import { Tooltip } from "@makeplane/propel/components/tooltip";
import { usePlatformOS } from "@/hooks/use-platform-os";
import packageJson from "package.json";
import { Button } from "@makeplane/propel/components/button";

export const WorkspaceEditionBadge = observer(function WorkspaceEditionBadge() {
  const { t } = useTranslation();
  const { isMobile } = usePlatformOS();

  return (
    <Tooltip label={`Version: v${packageJson.version}`} disabled={isMobile}>
      <Button
        variant="tertiary"
        size="md"
        stretch="auto"
        label="Self-hosted"
        aria-label={t("aria_labels.projects_sidebar.edition_badge")}
      />
    </Tooltip>
  );
});
