# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import uuid

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from plane.authentication.adapter.error import (
    AUTHENTICATION_ERROR_CODES,
    AuthenticationException,
)
from plane.authentication.provider.oauth.saml import SAMLProvider
from plane.authentication.utils.host import base_host
from plane.authentication.utils.login import user_login
from plane.authentication.utils.redirection_path import get_redirection_path
from plane.authentication.utils.user_auth_workflow import post_user_auth_workflow
from plane.license.models import Instance
from plane.utils.path_validator import get_safe_redirect_url


class SAMLInitiateEndpoint(View):
    def get(self, request):
        request.session["host"] = base_host(request=request, is_app=True)
        next_path = request.GET.get("next_path")
        if next_path:
            request.session["next_path"] = str(next_path)

        instance = Instance.objects.first()
        if instance is None or not instance.is_setup_done:
            exc = AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["INSTANCE_NOT_CONFIGURED"],
                error_message="INSTANCE_NOT_CONFIGURED",
            )
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True), next_path=next_path, params=exc.get_error_dict()
            )
            return HttpResponseRedirect(url)

        try:
            state = uuid.uuid4().hex
            provider = SAMLProvider(request=request, state=state)
            request.session["state"] = state
            return HttpResponseRedirect(provider.get_auth_url())
        except AuthenticationException as e:
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True), next_path=next_path, params=e.get_error_dict()
            )
            return HttpResponseRedirect(url)


@method_decorator(csrf_exempt, name="dispatch")
class SAMLCallbackEndpoint(View):
    def post(self, request):
        return self._complete(request)

    def get(self, request):
        return self._complete(request)

    def _complete(self, request):
        saml_response = request.POST.get("SAMLResponse") or request.GET.get("SAMLResponse")
        relay_state = request.POST.get("RelayState") or request.GET.get("RelayState")
        next_path = request.session.get("next_path")
        expected = request.session.get("state", "")
        if expected and relay_state and relay_state != expected:
            exc = AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True), next_path=next_path, params=exc.get_error_dict()
            )
            return HttpResponseRedirect(url)
        if not saml_response:
            exc = AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True), next_path=next_path, params=exc.get_error_dict()
            )
            return HttpResponseRedirect(url)
        try:
            provider = SAMLProvider(
                request=request, saml_response=saml_response, callback=post_user_auth_workflow
            )
            user = provider.authenticate()
            user_login(request=request, user=user, is_app=True)
            path = next_path or get_redirection_path(user=user)
            url = get_safe_redirect_url(base_url=base_host(request=request, is_app=True), next_path=path, params={})
            return HttpResponseRedirect(url)
        except AuthenticationException as e:
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True), next_path=next_path, params=e.get_error_dict()
            )
            return HttpResponseRedirect(url)
