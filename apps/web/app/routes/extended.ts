/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { layout, route } from "@react-router/dev/routes";
import type { RouteConfigEntry } from "@react-router/dev/routes";

const WORKSPACE_SETTINGS_DIR = "./(all)/[workspaceSlug]/(settings)/settings/(workspace)";
const PROJECT_SETTINGS_DIR = "./(all)/[workspaceSlug]/(settings)/settings/projects";

const WORKSPACE_SETTINGS_PAGES = [
  "issue-types",
  "wiki",
  "teamspaces",
  "initiatives",
  "dashboards",
  "customers",
  "project-templates",
  "roles",
  "audit",
  "scim",
];

const PROJECT_SETTINGS_PAGES = ["properties", "workflows", "templates", "time-tracking", "slas", "intake-forms"];

// Layout files mirror core.ts so mergeRoutes nests these under the existing settings layouts.
export const extendedRoutes: RouteConfigEntry[] = [
  layout("./(all)/layout.tsx", [
    layout("./(all)/[workspaceSlug]/layout.tsx", [
      layout("./(all)/[workspaceSlug]/(settings)/layout.tsx", [
        layout(
          `${WORKSPACE_SETTINGS_DIR}/layout.tsx`,
          WORKSPACE_SETTINGS_PAGES.map((page) =>
            route(`:workspaceSlug/settings/${page}`, `${WORKSPACE_SETTINGS_DIR}/${page}/page.tsx`)
          )
        ),
        layout(`${PROJECT_SETTINGS_DIR}/layout.tsx`, [
          layout(
            `${PROJECT_SETTINGS_DIR}/[projectId]/layout.tsx`,
            PROJECT_SETTINGS_PAGES.map((page) =>
              route(
                `:workspaceSlug/settings/projects/:projectId/${page}`,
                `${PROJECT_SETTINGS_DIR}/[projectId]/${page}/page.tsx`
              )
            )
          ),
        ]),
      ]),
    ]),
  ]),
];
