# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from django.core.management import call_command

from plane.license.models import InstanceConfiguration
from plane.license.utils.encryption import decrypt_data


@pytest.mark.unit
@pytest.mark.django_db
class TestConfigureInstance:
    """Template deploys have no /god-mode: the environment is the source of
    truth for instance configuration, on every boot."""

    def _run(self, monkeypatch, **env):
        monkeypatch.setenv("SECRET_KEY", "configure-instance-test")
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        call_command("configure_instance")

    def test_env_overrides_existing_row(self, monkeypatch):
        InstanceConfiguration.objects.create(key="ENABLE_MAGIC_LINK_LOGIN", value="0")
        self._run(monkeypatch, ENABLE_MAGIC_LINK_LOGIN="1")
        assert InstanceConfiguration.objects.get(key="ENABLE_MAGIC_LINK_LOGIN").value == "1"

    def test_row_is_kept_when_env_is_absent(self, monkeypatch):
        InstanceConfiguration.objects.create(key="ENABLE_MAGIC_LINK_LOGIN", value="0")
        monkeypatch.delenv("ENABLE_MAGIC_LINK_LOGIN", raising=False)
        self._run(monkeypatch)
        assert InstanceConfiguration.objects.get(key="ENABLE_MAGIC_LINK_LOGIN").value == "0"

    def test_null_string_means_unset(self, monkeypatch):
        # Platform Email injects "null" where it has no SMTP login.
        self._run(monkeypatch, EMAIL_HOST="null", EMAIL_FROM="None")
        assert InstanceConfiguration.objects.get(key="EMAIL_HOST").value == ""
        assert InstanceConfiguration.objects.get(key="EMAIL_FROM").value == ""

    def test_encrypted_key_from_env(self, monkeypatch):
        self._run(monkeypatch, EMAIL_HOST_PASSWORD="s3cret")
        row = InstanceConfiguration.objects.get(key="EMAIL_HOST_PASSWORD")
        assert row.is_encrypted is True
        assert decrypt_data(row.value) == "s3cret"
