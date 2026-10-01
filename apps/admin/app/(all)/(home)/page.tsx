/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
// components
import { LogoSpinner } from "@/components/common/logo-spinner";
import { InstanceFailureView } from "@/components/instance/failure";
// hooks
import { useInstance } from "@/hooks/store";
// components
import type { Route } from "./+types/page";
import { InstanceSignInForm } from "./sign-in-form";

function HomePage() {
  // store hooks
  const { instance, error } = useInstance();

  // if instance is not fetched, show loading
  if (!instance && !error) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <LogoSpinner />
      </div>
    );
  }

  // if instance fetch fails, show failure view
  if (error) {
    return <InstanceFailureView />;
  }

  // Instance admin is created from ADMIN_EMAIL / ADMIN_PASSWORD. No god-mode wizard.
  return <InstanceSignInForm />;
}

export default observer(HomePage);

export const meta: Route.MetaFunction = () => [
  { title: "Admin – Sign-In" },
  { name: "description", content: "Sign in to the Plane admin portal." },
];
