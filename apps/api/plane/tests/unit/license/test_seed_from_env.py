# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from django.utils import timezone

from plane.db.models import User, Workspace, WorkspaceMember
from plane.license.models import Instance, InstanceAdmin
from plane.license.utils.seed_from_env import seed_instance_from_env


@pytest.mark.unit
@pytest.mark.django_db
class TestSeedFromEnv:
    def _instance(self):
        return Instance.objects.create(
            instance_name="Unready",
            instance_id="seed-test-instance",
            current_version="1.0.0",
            last_checked_at=timezone.now(),
            is_setup_done=False,
        )

    def test_skip_without_admin_env(self, monkeypatch):
        self._instance()
        monkeypatch.delenv("ADMIN_EMAIL", raising=False)
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
        result = seed_instance_from_env()
        assert result["skipped"] is True
        assert InstanceAdmin.objects.count() == 0

    def test_seeds_admin_and_workspace(self, monkeypatch):
        self._instance()
        monkeypatch.setattr(
            "plane.bgtasks.workspace_seed_task.workspace_seed.delay",
            lambda *args, **kwargs: None,
        )
        monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
        monkeypatch.setenv("ADMIN_PASSWORD", "KuberoQaPlaneAdmin1!")
        monkeypatch.setenv("ADMIN_FIRST_NAME", "Admin")
        monkeypatch.setenv("INSTANCE_NAME", "Plane")
        monkeypatch.setenv("WORKSPACE_NAME", "Plane")
        monkeypatch.setenv("WORKSPACE_SLUG", "plane")

        result = seed_instance_from_env()
        assert result["skipped"] is False
        assert result["admin_created"] is True
        assert result["workspace_created"] is True
        assert result["workspace_slug"] == "plane"

        instance = Instance.objects.first()
        assert instance.is_setup_done is True
        user = User.objects.get(email="admin@example.com")
        assert InstanceAdmin.objects.filter(user=user, instance=instance).exists()
        workspace = Workspace.objects.get(slug="plane")
        assert WorkspaceMember.objects.filter(workspace=workspace, member=user, role=20).exists()
        assert user.profile.is_onboarded is True

        again = seed_instance_from_env()
        assert again["admin_created"] is False
        assert again["workspace_created"] is False
        assert Workspace.objects.count() == 1
