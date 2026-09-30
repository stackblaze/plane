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
      title="Workflows"
      description="State machines with optional approval. Multiple workflows can be attached to a project."
      listPath={`workspaces/${workspaceSlug}/projects/${projectId}/workflows/`}
      extraCreate={{ is_default: true }}
    />
  );
}
