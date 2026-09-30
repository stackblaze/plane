/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { ExtNamedList } from "@/components/settings/ext-named-list";
import type { Route } from "./+types/page";

export default function Page({ params }: Route.ComponentProps) {
  const { workspaceSlug } = params;
  return (
    <ExtNamedList
      title="Work item types"
      description="Define types such as Bug, Story, or Epic. Epics use the epic flag on the type."
      listPath={`workspaces/${workspaceSlug}/issue-types/`}
    />
  );
}
