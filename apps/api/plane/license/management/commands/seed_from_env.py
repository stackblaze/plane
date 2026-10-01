# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.core.management.base import BaseCommand

from plane.license.utils.seed_from_env import seed_instance_from_env


class Command(BaseCommand):
    help = "Seed instance admin and first workspace from ADMIN_* / WORKSPACE_* env"

    def handle(self, *args, **options):
        result = seed_instance_from_env()
        if result.get("skipped"):
            self.stdout.write("seed_from_env: skipped (ADMIN_EMAIL/PASSWORD or instance missing)")
            return
        if result.get("admin_created"):
            self.stdout.write(self.style.SUCCESS(f"seed_from_env: created admin {result.get('email')}"))
        else:
            self.stdout.write(f"seed_from_env: admin ready {result.get('email')}")
        if result.get("workspace_created"):
            self.stdout.write(
                self.style.SUCCESS(f"seed_from_env: created workspace /{result.get('workspace_slug')}")
            )
