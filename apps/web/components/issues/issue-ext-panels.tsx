/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { Button } from "@makeplane/propel/components/button";
import { extService } from "@/services/ext.service";

type Props = {
  workspaceSlug: string;
  projectId: string;
  issueId: string;
  disabled?: boolean;
};

type PropertyDef = { id: string; name: string; property_type: string };
type PropertyVal = { definition: string; value: { text?: string } };
type Worklog = { id: string; duration_minutes: number; logged_on: string; description: string };

export function IssueExtPanels(props: Props) {
  const { workspaceSlug, projectId, issueId, disabled } = props;
  const [defs, setDefs] = useState<PropertyDef[]>([]);
  const [values, setValues] = useState<PropertyVal[]>([]);
  const [logs, setLogs] = useState<Worklog[]>([]);
  const [minutes, setMinutes] = useState("30");
  const [note, setNote] = useState("");
  const [timerOn, setTimerOn] = useState(false);

  const reload = () => {
    extService
      .list(`workspaces/${workspaceSlug}/projects/${projectId}/custom-properties/`)
      .then(setDefs)
      .catch(() => undefined);
    extService
      .list(`workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/custom-properties/`)
      .then(setValues)
      .catch(() => undefined);
    extService
      .list(`workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/worklogs/`)
      .then(setLogs)
      .catch(() => undefined);
    extService
      .list(`workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/timer/`)
      .then((timer) => setTimerOn(Boolean(timer?.id)))
      .catch(() => undefined);
  };

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceSlug, projectId, issueId]);

  return (
    <div className="space-y-6 pt-4">
      <section className="space-y-2">
        <div className="text-14 font-medium">Custom properties</div>
        {defs.length === 0 && <div className="text-12 text-tertiary">No properties on this project yet.</div>}
        {defs.map((def) => {
          const current = values.find((value) => value.definition === def.id)?.value?.text || "";
          return (
            <label key={def.id} className="flex items-center gap-3 text-12">
              <span className="w-40 shrink-0">{def.name}</span>
              <input
                className="w-full rounded border border-subtle bg-transparent px-2 py-1"
                defaultValue={current}
                disabled={disabled}
                onBlur={(event) => {
                  void extService.create(
                    `workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/custom-properties/`,
                    { definition: def.id, value: { text: event.target.value } }
                  );
                }}
              />
            </label>
          );
        })}
      </section>
      <section className="space-y-2">
        <div className="text-14 font-medium">Time tracking</div>
        <div className="flex flex-wrap items-center gap-2">
          <input
            className="w-24 rounded border border-subtle bg-transparent px-2 py-1 text-12"
            value={minutes}
            disabled={disabled}
            onChange={(event) => setMinutes(event.target.value)}
            aria-label="Minutes"
          />
          <input
            className="min-w-40 flex-1 rounded border border-subtle bg-transparent px-2 py-1 text-12"
            value={note}
            disabled={disabled}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Note"
          />
          <Button
            variant="secondary"
            size="sm"
            disabled={disabled}
            label="Log time"
            onClick={() => {
              void extService
                .create(`workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/worklogs/`, {
                  duration_minutes: Number(minutes) || 0,
                  logged_on: new Date().toISOString().slice(0, 10),
                  description: note,
                })
                .then(reload);
            }}
          />
          <Button
            variant="secondary"
            size="sm"
            disabled={disabled}
            label={timerOn ? "Stop timer" : "Start timer"}
            onClick={() => {
              const path = `workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/timer/`;
              const action = timerOn ? extService.remove(path) : extService.create(path, { description: note });
              void action.then(reload);
            }}
          />
        </div>
        <ul className="space-y-1 text-12 text-tertiary">
          {logs.map((log) => (
            <li key={log.id}>
              {log.logged_on} · {log.duration_minutes}m {log.description}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
