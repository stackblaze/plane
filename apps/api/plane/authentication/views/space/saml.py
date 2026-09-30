# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import uuid

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from plane.authentication.adapter.error import (
    AUTHENTICATION_ERROR_CODES,
    AuthenticationException,
)
from plane.authentication.provider.oauth.saml import SAMLProvider
from plane.authentication.utils.host import base_host
from plane.authentication.utils.login import user_login
from plane.license.models import Instance
from plane.utils.path_validator import get_allowed_hosts, get_safe_redirect_url, validate_next_path


class SAMLInitiateSpaceEndpoint(View):
    def get(self, request):
        request.session["host"] = base_host(request=request, is_space=True)
        next_path = request.GET.get("next_path")
        instance = Instance.objects.first()
        if instance is None or not instance.is_setup_done:
            exc = AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["INSTANCE_NOT_CONFIGURED"],
                error_message="INSTANCE_NOT_CONFIGURED",
            )
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_space=True), next_path=next_path, params=exc.get_error_dict()
            )
            return HttpResponseRedirect(url)
        try:
            state = uuid.uuid4().hex
            provider = SAMLProvider(request=request, state=state)
            request.session["state"] = state
            return HttpResponseRedirect(provider.get_auth_url())
        except AuthenticationException as e:
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_space=True), next_path=next_path, params=e.get_error_dict()
            )
            return HttpResponseRedirect(url)


@method_decorator(csrf_exempt, name="dispatch")
class SAMLCallbackSpaceEndpoint(View):
    def post(self, request):
        return self._complete(request)

    def get(self, request):
        return self._complete(request)

    def _complete(self, request):
        saml_response = request.POST.get("SAMLResponse") or request.GET.get("SAMLResponse")
        next_path = request.session.get("next_path")
        if not saml_response:
            exc = AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SAML_PROVIDER_ERROR"],
                error_message="SAML_PROVIDER_ERROR",
            )
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_space=True), next_path=next_path, params=exc.get_error_dict()
            )
            return HttpResponseRedirect(url)
        try:
            provider = SAMLProvider(request=request, saml_response=saml_response)
            user = provider.authenticate()
            user_login(request=request, user=user, is_space=True)
            next_path = validate_next_path(next_path=next_path)
            url = f"{base_host(request=request, is_space=True).rstrip('/')}{next_path}"
            if url_has_allowed_host_and_scheme(url, allowed_hosts=get_allowed_hosts()):
                return HttpResponseRedirect(url)
            return HttpResponseRedirect(base_host(request=request, is_space=True))
        except AuthenticationException as e:
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_space=True), next_path=next_path, params=e.get_error_dict()
            )
            return HttpResponseRedirect(url)
