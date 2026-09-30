/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { ExtNamedList } from "@/components/settings/ext-named-list";
import type { Route } from "./+types/page";

export default function Page({ params }: Route.ComponentProps) {
  const { workspaceSlug, projectId } = params;
  return (
    <ExtNamedList
      title="Custom properties"
      description="Project-level fields on work items. Workspace-level properties use the same tables."
      listPath={`workspaces/${workspaceSlug}/projects/${projectId}/custom-properties/`}
      extraCreate={{ property_type: "text" }}
    />
  );
}
