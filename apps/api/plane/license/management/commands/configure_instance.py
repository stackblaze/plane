# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import os

# Django imports
from django.core.management.base import BaseCommand, CommandError

# Module imports
from plane.license.models import InstanceConfiguration
from plane.utils.instance_config_variables import instance_config_variables


# Platform add-ons inject a setting they cannot provide as the string "null"
# (Platform Email on an environment without an SMTP login). Plane would read
# that as a configured SMTP host and offer a magic code it cannot send.
_UNSET_VALUES = {"", "null", "none", "undefined"}


def env_value(item: dict) -> str:
    """Current value for a config item: the environment at run time, else
    the import-time default."""
    value = os.environ.get(item.get("key"), item.get("value"))
    if isinstance(value, str) and value.strip().lower() in _UNSET_VALUES:
        return ""
    return value


class Command(BaseCommand):
    help = "Configure instance variables"

    def handle(self, *args, **options):
        from plane.license.utils.encryption import encrypt_data

        mandatory_keys = ["SECRET_KEY"]

        for item in mandatory_keys:
            if not os.environ.get(item):
                raise CommandError(f"{item} env variable is required.")

        for item in instance_config_variables:
            key = item.get("key")
            obj, created = InstanceConfiguration.objects.get_or_create(key=key)
            # The environment is the source of truth: template deploys have no
            # /god-mode, so a key set in the environment overrides the stored
            # row on every boot. A key absent from the environment keeps
            # whatever the row holds (the import-time default on creation).
            if not created and key not in os.environ:
                self.stdout.write(self.style.WARNING(f"{obj.key} configuration already exists"))
                continue
            value = env_value(item)
            obj.category = item.get("category")
            obj.is_encrypted = item.get("is_encrypted", False)
            obj.value = encrypt_data(value) if obj.is_encrypted else value
            obj.save()
            self.stdout.write(self.style.SUCCESS(f"{obj.key} loaded with value from environment variable."))
