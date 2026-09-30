# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from plane.db.models import Workspace
from plane.db.models.ext import AuditLog
from plane.utils.ip_address import get_client_ip


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method not in ("POST", "PATCH", "PUT", "DELETE"):
            return response
        if not request.path.startswith("/api/"):
            return response
        if request.path.startswith("/api/scim/") or request.path.startswith("/api/intake-"):
            return response
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return response
        parts = request.path.strip("/").split("/")
        workspace = None
        if len(parts) >= 3 and parts[1] == "workspaces":
            workspace = Workspace.objects.filter(slug=parts[2]).first()
        if not workspace:
            return response
        try:
            AuditLog.objects.create(
                workspace=workspace,
                actor=user,
                method=request.method,
                path=request.path[:512],
                status_code=response.status_code,
                ip_address=get_client_ip(request),
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
                body={},
            )
        except Exception:
            pass
        return response
