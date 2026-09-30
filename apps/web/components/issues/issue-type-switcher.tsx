/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { useIssueDetail } from "@/hooks/store/use-issue-detail";
import { IssueIdentifier } from "@/components/issues/issue-detail/issue-identifier";
import { extService } from "@/services/ext.service";

export type TIssueTypeSwitcherProps = {
  issueId: string;
  disabled: boolean;
};

type TIssueType = {
  id: string;
  name: string;
  is_epic?: boolean;
  issue_type?: string;
};

export const IssueTypeSwitcher = observer(function IssueTypeSwitcher(props: TIssueTypeSwitcherProps) {
  const { issueId, disabled } = props;
  const { workspaceSlug } = useParams();
  const {
    issue: { getIssueById },
    updateIssue,
  } = useIssueDetail();
  const issue = getIssueById(issueId);
  const [types, setTypes] = useState<TIssueType[]>([]);

  useEffect(() => {
    if (!workspaceSlug || !issue?.project_id) return;
    extService
      .list(`workspaces/${workspaceSlug}/projects/${issue.project_id}/issue-types/`)
      .then((rows: Array<{ id: string; issue_type: string }>) => {
        if (!rows?.length) {
          return extService.list(`workspaces/${workspaceSlug}/issue-types/`).then((all: TIssueType[]) => setTypes(all || []));
        }
        return extService.list(`workspaces/${workspaceSlug}/issue-types/`).then((all: TIssueType[]) => {
          const enabled = new Set(rows.map((row) => row.issue_type));
          setTypes((all || []).filter((type) => enabled.has(type.id)));
        });
      })
      .catch(() => undefined);
  }, [workspaceSlug, issue?.project_id]);

  if (!issue || !issue.project_id) return <></>;

  const current = types.find((type) => type.id === issue.type_id);

  return (
    <div className="flex items-center gap-2">
      <IssueIdentifier issueId={issueId} projectId={issue.project_id} size="md" enableClickToCopyIdentifier />
      {types.length > 0 && (
        <select
          className="rounded border border-subtle bg-transparent px-2 py-1 text-12"
          disabled={disabled}
          value={issue.type_id || ""}
          aria-label="Work item type"
          onChange={(event) => {
            const typeId = event.target.value || null;
            void extService
              .create(`workspaces/${workspaceSlug}/projects/${issue.project_id}/issues/${issueId}/type/`, {
                type_id: typeId,
              })
              .then(() => updateIssue(String(workspaceSlug), issue.project_id as string, issueId, { type_id: typeId }));
          }}
        >
          <option value="">{current?.name || "Type"}</option>
          {types.map((type) => (
            <option key={type.id} value={type.id}>
              {type.name}
              {type.is_epic ? " (Epic)" : ""}
            </option>
          ))}
        </select>
      )}
    </div>
  );
});
