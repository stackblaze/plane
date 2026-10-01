# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, override_settings

from plane.authentication.utils.host import base_host as auth_base_host
from plane.utils.host import base_host, request_origin


def _request(**headers):
    return RequestFactory().post("/auth/sign-in/", **headers)


@pytest.mark.unit
class TestRequestOrigin:
    def test_forwarded_headers_win(self):
        req = _request(
            HTTP_HOST="api.internal:8000",
            HTTP_X_FORWARDED_HOST="plane.example.com",
            HTTP_X_FORWARDED_PROTO="https",
        )
        assert request_origin(req) == "https://plane.example.com"

    def test_falls_back_to_host_and_request_scheme(self):
        req = _request(HTTP_HOST="plane.example.com")
        assert request_origin(req) == "http://plane.example.com"

    def test_empty_without_a_host(self):
        req = _request()
        req.META.pop("HTTP_HOST", None)
        req.META.pop("SERVER_NAME", None)
        assert request_origin(req) == ""


@pytest.mark.unit
class TestBaseHostFallback:
    """A template deploy serves web, api and spaces from one origin behind the
    proxy; when WEB_URL is not set, the request's origin is the web app."""

    @override_settings(WEB_URL=None, APP_BASE_URL=None, SPACE_BASE_URL=None, ADMIN_BASE_URL=None)
    def test_app_redirect_uses_the_request_origin(self):
        req = _request(HTTP_HOST="plane.example.com", HTTP_X_FORWARDED_PROTO="https")
        assert auth_base_host(req, is_app=True) == "https://plane.example.com"
        assert base_host(req, is_app=True) == "https://plane.example.com"
        assert base_host(req, is_space=True) == "https://plane.example.com/spaces/"

    @override_settings(WEB_URL="https://configured.example.com", APP_BASE_URL=None)
    def test_configured_web_url_still_wins(self):
        req = _request(HTTP_HOST="plane.example.com", HTTP_X_FORWARDED_PROTO="https")
        assert auth_base_host(req, is_app=True) == "https://configured.example.com"
        assert base_host(req, is_app=True) == "https://configured.example.com"

    @override_settings(WEB_URL=None, APP_BASE_URL=None)
    def test_still_improperly_configured_without_any_host(self):
        req = _request()
        req.META.pop("HTTP_HOST", None)
        req.META.pop("SERVER_NAME", None)
        with pytest.raises(ImproperlyConfigured):
            base_host(req, is_app=True)
