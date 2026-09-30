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
      title="Work item templates"
      description="Field snapshots you can apply or schedule as recurring work items."
      listPath={`workspaces/${workspaceSlug}/projects/${projectId}/work-item-templates/`}
      extraCreate={{ payload: { name: "Untitled" } }}
    />
  );
}
