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

import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

# Any constant shared by every pod of the instance ("plane-migrate").
LOCK_KEY = 0x706C616E65
POLL_SECONDS = 3


class Command(BaseCommand):
    help = "Run migrate while holding a Postgres advisory lock"

    def handle(self, *args, **options):
        # Poll with pg_try_advisory_lock, never block in pg_advisory_lock.
        # A pod blocked inside pg_advisory_lock is an open statement, and
        # CREATE INDEX CONCURRENTLY (migration 0103, atomic=False) waits for
        # every open transaction to finish: the lock holder then waits for
        # the waiter forever (an undetected deadlock), the startup probe
        # kills it mid-migration, and the half-applied index makes every
        # later start fail with "relation ... already exists".
        self.stdout.write("Waiting for the migration lock")
        while True:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_try_advisory_lock(%s)", [LOCK_KEY])
                if cursor.fetchone()[0]:
                    break
            time.sleep(POLL_SECONDS)
        try:
            call_command("migrate", interactive=False)
        finally:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [LOCK_KEY])
