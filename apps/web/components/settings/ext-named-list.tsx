/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { Button } from "@makeplane/propel/components/button";
import { SettingsContentWrapper } from "@/components/settings/content-wrapper";
import { SettingsHeading } from "@/components/settings/heading";
import { extService } from "@/services/ext.service";

type Item = { id: string; name?: string; path?: string; method?: string; [key: string]: unknown };

type Props = {
  title: string;
  description: string;
  listPath: string;
  createPath?: string;
  extraCreate?: Record<string, unknown>;
  header?: React.ReactNode;
  nameKey?: string;
};

export function ExtNamedList(props: Props) {
  const { title, description, listPath, createPath, extraCreate, header, nameKey = "name" } = props;
  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState("");

  const reload = () => {
    extService
      .list(listPath)
      .then((rows) => setItems(rows || []))
      .catch(() => setItems([]));
  };

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listPath]);

  return (
    <SettingsContentWrapper header={header}>
      <SettingsHeading title={title} description={description} />
      <div className="flex items-center gap-2 py-4">
        <input
          className="w-64 rounded border border-subtle bg-transparent px-2 py-1 text-13"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder={`New ${title.toLowerCase()}`}
        />
        <Button
          variant="primary"
          size="sm"
          label="Add"
          onClick={() => {
            if (!name.trim()) return;
            void extService.create(createPath || listPath, { [nameKey]: name, ...(extraCreate || {}) }).then(() => {
              setName("");
              reload();
            });
          }}
        />
      </div>
      <ul className="divide-y divide-subtle">
        {items.map((item) => (
          <li key={item.id} className="flex items-center justify-between py-2 text-13">
            <span>
              {String(item[nameKey] || item.path || item.id)}
              {item.method ? ` ${item.method}` : ""}
            </span>
            <Button
              variant="tertiary"
              size="sm"
              label="Remove"
              onClick={() => {
                void extService.remove(`${createPath || listPath}${item.id}/`).then(reload);
              }}
            />
          </li>
        ))}
        {items.length === 0 && <li className="py-6 text-12 text-tertiary">Nothing here yet.</li>}
      </ul>
    </SettingsContentWrapper>
  );
}
