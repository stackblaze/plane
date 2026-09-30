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
      title="Intake forms"
      description="Public forms and inbound email addresses that create intake items."
      listPath={`workspaces/${workspaceSlug}/projects/${projectId}/intake-forms/`}
    />
  );
}
