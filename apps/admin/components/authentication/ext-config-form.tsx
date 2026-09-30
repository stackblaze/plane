/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { isEmpty } from "lodash-es";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { API_BASE_URL } from "@plane/constants";
import { Button } from "@makeplane/propel/components/button";
import { setToast } from "@plane/blocks/toast";
import type { IFormattedInstanceConfiguration } from "@plane/types";
import { ConfirmDiscardModal } from "@/components/common/confirm-discard-modal";
import { ControllerInput } from "@/components/common/controller-input";
import { ControllerSwitch } from "@/components/common/controller-switch";
import { CopyField } from "@/components/common/copy-field";
import { useInstance } from "@/hooks/store";

type Field = {
  key: string;
  type: "text" | "password";
  label: string;
  required?: boolean;
};

type Props = {
  config: IFormattedInstanceConfiguration;
  title: string;
  enableKey: string;
  fields: Field[];
  callbackPath: string;
};

export function InstanceExtConfigForm(props: Props) {
  const { config, title, enableKey, fields, callbackPath } = props;
  const [isDiscardChangesModalOpen, setIsDiscardChangesModalOpen] = useState(false);
  const { updateInstanceConfigurations } = useInstance();
  const defaultValues = Object.fromEntries(
    [...fields.map((field) => [field.key, config[field.key as keyof IFormattedInstanceConfiguration] || ""]), [enableKey, config[enableKey as keyof IFormattedInstanceConfiguration] || "0"]]
  );
  const {
    handleSubmit,
    control,
    reset,
    formState: { isDirty, isSubmitting },
  } = useForm<Record<string, string>>({ defaultValues });

  const originURL = !isEmpty(API_BASE_URL) ? API_BASE_URL : typeof window !== "undefined" ? window.location.origin : "";

  const onSubmit = async (formData: Record<string, string>) => {
    try {
      const response = await updateInstanceConfigurations(formData);
      setToast({ type: "success", title: "Done!", message: `${title} authentication is configured.` });
      reset(
        Object.fromEntries(
          Object.keys(defaultValues).map((key) => [key, response.find((item) => item.key === key)?.value || ""])
        )
      );
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <ConfirmDiscardModal
        isOpen={isDiscardChangesModalOpen}
        onDiscardHref="/authentication"
        handleClose={() => setIsDiscardChangesModalOpen(false)}
      />
      <div className="grid w-full grid-cols-2 gap-x-12 gap-y-8">
        <div className="col-span-2 flex flex-col gap-y-4 pt-1 md:col-span-1">
          <div className="pt-2.5 text-18 font-medium">{title} details for Plane</div>
          {fields.map((field) => (
            <ControllerInput
              key={field.key}
              control={control}
              type={field.type}
              name={field.key}
              label={field.label}
              placeholder=""
              error={false}
              required={field.required}
            />
          ))}
          <ControllerSwitch control={control} field={{ name: enableKey, label: title }} />
          <div className="flex items-center gap-4 pt-4">
            <Button
              variant="primary"
              size="md"
              stretch="auto"
              onClick={(e) => void handleSubmit(onSubmit)(e)}
              loading={isSubmitting}
              disabled={!isDirty}
              label={isSubmitting ? "Saving" : "Save changes"}
            />
            <Button
              variant="secondary"
              size="md"
              stretch="auto"
              nativeButton={false}
              render={<Link href="/authentication" />}
              label="Go back"
            />
          </div>
        </div>
        <div className="col-span-2 flex flex-col gap-y-6 md:col-span-1">
          <div className="pt-2 text-18 font-medium">Callback</div>
          <div className="flex flex-col gap-y-4 rounded-lg bg-layer-1 px-6 py-4">
            <CopyField key="callback" label="Callback URI" url={`${originURL}${callbackPath}`} description={<p>Register this URL with your identity provider.</p>} />
          </div>
        </div>
      </div>
    </>
  );
}
