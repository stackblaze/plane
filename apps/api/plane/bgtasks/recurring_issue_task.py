# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from plane.db.models import Issue
from plane.db.models.ext import RecurringIssue
from plane.utils.exception_logger import log_exception


@shared_task
def spawn_recurring_issues():
    now = timezone.now()
    try:
        schedules = RecurringIssue.objects.filter(is_active=True, next_run_at__lte=now).select_related("template")
        for schedule in schedules:
            payload = dict(schedule.template.payload or {})
            name = payload.get("name") or schedule.template.name
            issue = Issue.objects.create(project_id=schedule.project_id, name=name)
            if payload.get("priority"):
                issue.priority = payload["priority"]
                issue.save(update_fields=["priority"])
            if payload.get("type"):
                issue.type_id = payload["type"]
                issue.save(update_fields=["type"])
            delta = {
                "daily": timedelta(days=1),
                "weekly": timedelta(days=7),
                "monthly": timedelta(days=30),
            }.get(schedule.cadence, timedelta(days=7))
            schedule.last_run_at = now
            schedule.next_run_at = now + delta
            schedule.save(update_fields=["last_run_at", "next_run_at"])
    except Exception as exc:
        log_exception(exc)
