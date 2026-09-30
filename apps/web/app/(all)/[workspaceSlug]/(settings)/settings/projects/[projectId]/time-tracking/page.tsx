/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { SettingsContentWrapper } from "@/components/settings/content-wrapper";
import { SettingsHeading } from "@/components/settings/heading";
import { extService } from "@/services/ext.service";
import type { Route } from "./+types/page";

export default function Page({ params }: Route.ComponentProps) {
  const { workspaceSlug, projectId } = params;
  const [rows, setRows] = useState<Array<{ user_id: string; issue_id: string; total_minutes: number }>>([]);
  useEffect(() => {
    extService
      .list(`workspaces/${workspaceSlug}/projects/${projectId}/worklog-report/`)
      .then(setRows)
      .catch(() => setRows([]));
  }, [workspaceSlug, projectId]);
  return (
    <SettingsContentWrapper>
      <SettingsHeading title="Time tracking" description="Hours logged against work items in this project." />
      <ul className="divide-y divide-subtle pt-4 text-13">
        {rows.map((row) => (
          <li key={`${row.user_id}-${row.issue_id}`} className="py-2">
            {row.total_minutes}m on {row.issue_id}
          </li>
        ))}
        {rows.length === 0 && <li className="py-6 text-12 text-tertiary">No time logged yet.</li>}
      </ul>
    </SettingsContentWrapper>
  );
}
