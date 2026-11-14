# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""`migrate` under a Postgres advisory lock (StackBlaze fork).

Without a separate migrator service the api runs the migrations itself. When
two api pods start together (a rollout during the first boot, or replicas > 1)
both ran `migrate` and one crashed on "relation ... already exists". This
holds a session-level advisory lock for the duration, so the second pod waits
and then finds nothing left to apply.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

# Any constant shared by every pod of the instance ("plane-migrate").
LOCK_KEY = 0x706C616E65


class Command(BaseCommand):
    help = "Run migrate while holding a Postgres advisory lock"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("Waiting for the migration lock")
            cursor.execute("SELECT pg_advisory_lock(%s)", [LOCK_KEY])
            try:
                call_command("migrate", interactive=False)
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [LOCK_KEY])
