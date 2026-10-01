# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Seed instance admin and a first workspace from environment variables.

Template deploys skip /god-mode: ADMIN_EMAIL + ADMIN_PASSWORD make the
instance ready and the web app shows login. Optional WORKSPACE_NAME /
WORKSPACE_SLUG create a workspace so the admin lands in the app.
"""

from __future__ import annotations

import os
import re
import uuid

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.text import slugify

from plane.db.models import Profile, User, Workspace, WorkspaceMember
from plane.license.models import Instance, InstanceAdmin
from plane.utils.constants import RESTRICTED_WORKSPACE_SLUGS


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _workspace_slug(name: str, explicit: str) -> str:
    slug = slugify(explicit or name) or "workspace"
    slug = re.sub(r"[^a-z0-9-]", "", slug)[:48] or "workspace"
    if slug in RESTRICTED_WORKSPACE_SLUGS:
        slug = f"{slug}-ws"[:48]
    return slug


def seed_instance_from_env() -> dict:
    """Create instance admin (and optional first workspace) from env.

    Returns a small result dict for the management command / tests.
    Missing ADMIN_EMAIL or ADMIN_PASSWORD is a no-op.
    """
    email = _env("ADMIN_EMAIL").lower()
    password = os.environ.get("ADMIN_PASSWORD") or ""
    first = _env("ADMIN_FIRST_NAME", "Admin") or "Admin"
    company = _env("INSTANCE_NAME", "Plane") or "Plane"
    result = {
        "skipped": False,
        "admin_created": False,
        "workspace_created": False,
        "email": email,
    }

    if not email or not password:
        result["skipped"] = True
        return result

    instance = Instance.objects.first()
    if instance is None:
        result["skipped"] = True
        return result

    user = User.objects.filter(email=email).first()
    if user is None:
        user = User.objects.create(
            first_name=first,
            last_name="",
            email=email,
            username=uuid.uuid4().hex,
            password=make_password(password),
            is_password_autoset=False,
            is_active=True,
            last_active=timezone.now(),
        )
        result["admin_created"] = True

    Profile.objects.get_or_create(user=user, defaults={"company_name": company})
    InstanceAdmin.objects.get_or_create(user=user, instance=instance)

    changed = []
    if not instance.is_setup_done:
        instance.is_setup_done = True
        changed.append("is_setup_done")
    if company and instance.instance_name != company:
        instance.instance_name = company
        changed.append("instance_name")
    if changed:
        instance.save()

    disable_ws = _env("DISABLE_WORKSPACE_CREATION", "0") == "1"
    workspace_name = _env("WORKSPACE_NAME", company)
    if not disable_ws and workspace_name and not Workspace.objects.exists():
        slug = _workspace_slug(workspace_name, _env("WORKSPACE_SLUG"))
        workspace = Workspace.objects.create(
            name=workspace_name[:80],
            slug=slug,
            owner=user,
            organization_size=_env("WORKSPACE_SIZE", "1-10") or "1-10",
        )
        WorkspaceMember.objects.get_or_create(
            workspace=workspace,
            member=user,
            defaults={"role": 20},
        )
        profile, _ = Profile.objects.get_or_create(user=user, defaults={"company_name": company})
        profile.is_onboarded = True
        profile.onboarding_step = {
            "profile_complete": True,
            "workspace_create": True,
            "workspace_invite": True,
            "workspace_join": True,
        }
        profile.last_workspace_id = workspace.id
        profile.company_name = company
        profile.save()
        result["workspace_created"] = True
        result["workspace_slug"] = slug
        try:
            from plane.bgtasks.workspace_seed_task import workspace_seed

            workspace_seed.delay(str(workspace.id))
        except Exception:
            pass

    return result
