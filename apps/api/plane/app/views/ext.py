# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from datetime import timedelta
from uuid import uuid4

from django.db.models import Sum
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from plane.app.permissions import ROLE, allow_permission
from plane.app.serializers.ext import (
    AccessRuleSerializer,
    AuditLogSerializer,
    CustomPropertySerializer,
    CustomPropertyValueSerializer,
    CustomRoleSerializer,
    CustomerIssueSerializer,
    CustomerSerializer,
    DashboardSerializer,
    DashboardWidgetSerializer,
    InitiativeIssueSerializer,
    InitiativeProjectSerializer,
    InitiativeSerializer,
    IntakeFormSerializer,
    IssueTypeSerializer,
    ProjectIssueTypeSerializer,
    ProjectTemplateSerializer,
    RecurringIssueSerializer,
    RoleAssignmentSerializer,
    SCIMTokenSerializer,
    SLAPolicySerializer,
    TeamspaceMemberSerializer,
    TeamspaceProjectSerializer,
    TeamspaceSerializer,
    WorkItemTemplateSerializer,
    WorkflowApprovalSerializer,
    WorkflowSerializer,
    WorkflowTransitionSerializer,
    WorklogSerializer,
    WorklogTimerSerializer,
)
from plane.app.views.base import BaseAPIView, BaseViewSet
from plane.db.models import (
    Cycle,
    CycleIssue,
    DeployBoard,
    Issue,
    IssueType,
    Page,
    Project,
    ProjectIssueType,
    State,
    Workspace,
    WorkspaceMember,
)
from plane.db.models.ext import (
    AccessRule,
    AuditLog,
    CustomProperty,
    CustomPropertyValue,
    CustomRole,
    Customer,
    CustomerIssue,
    Dashboard,
    DashboardWidget,
    Initiative,
    InitiativeIssue,
    InitiativeProject,
    IntakeForm,
    RecurringIssue,
    RoleAssignment,
    SCIMToken,
    SLAPolicy,
    Teamspace,
    TeamspaceMember,
    TeamspaceProject,
    WorkItemTemplate,
    Workflow,
    WorkflowApproval,
    WorkflowTransition,
    Worklog,
    WorklogTimer,
    ProjectTemplate,
)
from plane.db.models.intake import Intake, IntakeIssue
from plane.utils.ip_address import get_client_ip


class IssueTypeViewSet(BaseViewSet):
    serializer_class = IssueTypeSerializer
    model = IssueType
    search_fields = ["name"]

    def get_queryset(self):
        return IssueType.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def partial_update(self, request, slug, pk):
        issue_type = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(issue_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectIssueTypeViewSet(BaseViewSet):
    serializer_class = ProjectIssueTypeSerializer
    model = ProjectIssueType

    def get_queryset(self):
        return ProjectIssueType.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id)
        Project.objects.filter(pk=project_id).update(is_issue_type_enabled=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueTypeAssignEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, issue_id):
        issue = Issue.objects.get(workspace__slug=slug, project_id=project_id, pk=issue_id)
        type_id = request.data.get("type_id")
        if type_id and not ProjectIssueType.objects.filter(project_id=project_id, issue_type_id=type_id).exists():
            return Response({"error": "Type is not enabled on this project"}, status=status.HTTP_400_BAD_REQUEST)
        issue.type_id = type_id
        issue.save(update_fields=["type"])
        return Response({"id": str(issue.id), "type_id": str(issue.type_id) if issue.type_id else None})


class CustomPropertyViewSet(BaseViewSet):
    serializer_class = CustomPropertySerializer
    model = CustomProperty

    def get_queryset(self):
        qs = CustomProperty.objects.filter(workspace__slug=self.kwargs["slug"])
        project_id = self.kwargs.get("project_id")
        if project_id:
            from django.db.models import Q

            qs = qs.filter(Q(project_id=project_id) | Q(is_workspace_level=True, project__isnull=True))
        return qs.distinct()

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug, project_id=None):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug, project_id=None):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id or request.data.get("project"))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def partial_update(self, request, slug, pk, project_id=None):
        obj = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk, project_id=None):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomPropertyValueViewSet(BaseViewSet):
    serializer_class = CustomPropertyValueSerializer
    model = CustomPropertyValue

    def get_queryset(self):
        return CustomPropertyValue.objects.filter(
            workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"], issue_id=self.kwargs["issue_id"]
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id, issue_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def create(self, request, slug, project_id, issue_id):
        workspace = Workspace.objects.get(slug=slug)
        obj, _ = CustomPropertyValue.objects.update_or_create(
            workspace=workspace,
            project_id=project_id,
            issue_id=issue_id,
            definition_id=request.data.get("definition"),
            defaults={"value": request.data.get("value", {})},
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class WorklogViewSet(BaseViewSet):
    serializer_class = WorklogSerializer
    model = Worklog

    def get_queryset(self):
        qs = Worklog.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])
        issue_id = self.kwargs.get("issue_id")
        if issue_id:
            qs = qs.filter(issue_id=issue_id)
        return qs

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id, issue_id=None):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def create(self, request, slug, project_id, issue_id=None):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            workspace=workspace,
            project_id=project_id,
            issue_id=issue_id or request.data.get("issue"),
            user=request.user,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def destroy(self, request, slug, project_id, pk, issue_id=None):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorklogTimerEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def get(self, request, slug, project_id, issue_id):
        timer = WorklogTimer.objects.filter(
            workspace__slug=slug, project_id=project_id, issue_id=issue_id, user=request.user
        ).first()
        if not timer:
            return Response({}, status=status.HTTP_200_OK)
        return Response(WorklogTimerSerializer(timer).data)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, issue_id):
        workspace = Workspace.objects.get(slug=slug)
        timer, created = WorklogTimer.objects.get_or_create(
            workspace=workspace,
            project_id=project_id,
            issue_id=issue_id,
            user=request.user,
            defaults={"started_at": timezone.now(), "description": request.data.get("description", "")},
        )
        if not created:
            return Response(WorklogTimerSerializer(timer).data)
        return Response(WorklogTimerSerializer(timer).data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def delete(self, request, slug, project_id, issue_id):
        timer = WorklogTimer.objects.filter(
            workspace__slug=slug, project_id=project_id, issue_id=issue_id, user=request.user
        ).first()
        if not timer:
            return Response(status=status.HTTP_404_NOT_FOUND)
        minutes = max(1, int((timezone.now() - timer.started_at).total_seconds() // 60))
        worklog = Worklog.objects.create(
            workspace_id=timer.workspace_id,
            project_id=project_id,
            issue_id=issue_id,
            user=request.user,
            duration_minutes=minutes,
            logged_on=timezone.now().date(),
            description=timer.description,
            started_at=timer.started_at,
            ended_at=timezone.now(),
        )
        timer.delete()
        return Response(WorklogSerializer(worklog).data)


class WorklogReportEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def get(self, request, slug, project_id):
        rows = (
            Worklog.objects.filter(workspace__slug=slug, project_id=project_id)
            .values("user_id", "issue_id")
            .annotate(total_minutes=Sum("duration_minutes"))
        )
        return Response(list(rows))


class TeamspaceViewSet(BaseViewSet):
    serializer_class = TeamspaceSerializer
    model = Teamspace

    def get_queryset(self):
        return Teamspace.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teamspace = serializer.save(workspace=workspace)
        TeamspaceMember.objects.create(workspace=workspace, teamspace=teamspace, member=request.user, role=20)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def partial_update(self, request, slug, pk):
        obj = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamspaceMemberViewSet(BaseViewSet):
    serializer_class = TeamspaceMemberSerializer
    model = TeamspaceMember

    def get_queryset(self):
        return TeamspaceMember.objects.filter(workspace__slug=self.kwargs["slug"], teamspace_id=self.kwargs["teamspace_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug, teamspace_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug, teamspace_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, teamspace_id=teamspace_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, teamspace_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamspaceProjectViewSet(BaseViewSet):
    serializer_class = TeamspaceProjectSerializer
    model = TeamspaceProject

    def get_queryset(self):
        return TeamspaceProject.objects.filter(workspace__slug=self.kwargs["slug"], teamspace_id=self.kwargs["teamspace_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug, teamspace_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug, teamspace_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, teamspace_id=teamspace_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, teamspace_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InitiativeViewSet(BaseViewSet):
    serializer_class = InitiativeSerializer
    model = Initiative

    def get_queryset(self):
        return Initiative.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        data = []
        for initiative in self.get_queryset():
            payload = self.get_serializer(initiative).data
            issue_ids = list(initiative.issues.values_list("issue_id", flat=True))
            issues = Issue.objects.filter(id__in=issue_ids)
            total = issues.count()
            done = issues.filter(state__group__in=["completed", "cancelled"]).count()
            payload["progress"] = {"total": total, "done": done}
            data.append(payload)
        return Response(data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def partial_update(self, request, slug, pk):
        obj = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InitiativeLinkEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def post(self, request, slug, pk):
        workspace = Workspace.objects.get(slug=slug)
        initiative = Initiative.objects.get(workspace=workspace, pk=pk)
        if request.data.get("project"):
            obj = InitiativeProject.objects.create(
                workspace=workspace, initiative=initiative, project_id=request.data["project"]
            )
            return Response(InitiativeProjectSerializer(obj).data, status=status.HTTP_201_CREATED)
        if request.data.get("issue"):
            obj = InitiativeIssue.objects.create(workspace=workspace, initiative=initiative, issue_id=request.data["issue"])
            return Response(InitiativeIssueSerializer(obj).data, status=status.HTTP_201_CREATED)
        return Response({"error": "project or issue is required"}, status=status.HTTP_400_BAD_REQUEST)


class DashboardViewSet(BaseViewSet):
    serializer_class = DashboardSerializer
    model = Dashboard

    def get_queryset(self):
        return Dashboard.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def retrieve(self, request, slug, pk):
        dashboard = self.get_queryset().get(pk=pk)
        payload = self.get_serializer(dashboard).data
        payload["widgets"] = DashboardWidgetSerializer(dashboard.widgets.all(), many=True).data
        return Response(payload)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardWidgetViewSet(BaseViewSet):
    serializer_class = DashboardWidgetSerializer
    model = DashboardWidget

    def get_queryset(self):
        return DashboardWidget.objects.filter(workspace__slug=self.kwargs["slug"], dashboard_id=self.kwargs["dashboard_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug, dashboard_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug, dashboard_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, dashboard_id=dashboard_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, dashboard_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExtCycleProgressEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def get(self, request, slug, project_id):
        cycles = Cycle.objects.filter(workspace__slug=slug, project_id=project_id, archived_at__isnull=True)
        today = timezone.now().date()
        payload = []
        for cycle in cycles:
            issues = Issue.objects.filter(issue_cycle__cycle=cycle)
            total = issues.count()
            done = issues.filter(state__group__in=["completed", "cancelled"]).count()
            is_active = bool(cycle.start_date and cycle.end_date and cycle.start_date.date() <= today <= cycle.end_date.date())
            payload.append(
                {
                    "id": str(cycle.id),
                    "name": cycle.name,
                    "is_active": is_active,
                    "total": total,
                    "done": done,
                    "progress": (done / total) if total else 0,
                }
            )
        return Response(payload)


class WikiPageViewSet(BaseViewSet):
    serializer_class = None
    model = Page

    def get_queryset(self):
        return Page.objects.filter(workspace__slug=self.kwargs["slug"], is_global=True)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        pages = self.get_queryset().values("id", "name", "parent_id", "is_global", "access", "sort_order")
        return Response(list(pages))

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        page = Page.objects.create(
            workspace=workspace,
            name=request.data.get("name", "Untitled"),
            owned_by=request.user,
            is_global=True,
            parent_id=request.data.get("parent"),
            access=request.data.get("access", 0),
        )
        return Response({"id": str(page.id), "name": page.name, "parent_id": str(page.parent_id) if page.parent_id else None})


class PublishEntityEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        entity_name = request.data.get("entity_name")
        entity_identifier = request.data.get("entity_identifier")
        if entity_name not in ("page", "view"):
            return Response({"error": "entity_name must be page or view"}, status=status.HTTP_400_BAD_REQUEST)
        board, _ = DeployBoard.objects.get_or_create(
            workspace=workspace,
            project_id=project_id,
            entity_name=entity_name,
            entity_identifier=entity_identifier,
            defaults={"is_comments_enabled": True},
        )
        return Response({"anchor": board.anchor, "entity_name": board.entity_name})

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def delete(self, request, slug, project_id):
        DeployBoard.objects.filter(
            workspace__slug=slug,
            project_id=project_id,
            entity_name=request.data.get("entity_name"),
            entity_identifier=request.data.get("entity_identifier"),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkflowViewSet(BaseViewSet):
    serializer_class = WorkflowSerializer
    model = Workflow

    def get_queryset(self):
        return Workflow.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkflowTransitionViewSet(BaseViewSet):
    serializer_class = WorkflowTransitionSerializer
    model = WorkflowTransition

    def get_queryset(self):
        return WorkflowTransition.objects.filter(workspace__slug=self.kwargs["slug"], workflow_id=self.kwargs["workflow_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id, workflow_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id, workflow_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id, workflow_id=workflow_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, workflow_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueWorkflowTransitionEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, issue_id):
        issue = Issue.objects.get(workspace__slug=slug, project_id=project_id, pk=issue_id)
        to_state_id = request.data.get("state")
        workflows = Workflow.objects.filter(project_id=project_id)
        if issue.type_id:
            typed = workflows.filter(issue_type_id=issue.type_id)
            workflows = typed or workflows.filter(is_default=True)
        else:
            workflows = workflows.filter(is_default=True)
        workflow = workflows.first()
        if not workflow:
            issue.state_id = to_state_id
            issue.save(update_fields=["state"])
            return Response({"id": str(issue.id), "state": str(issue.state_id)})

        transition = WorkflowTransition.objects.filter(
            workflow=workflow, from_state_id=issue.state_id, to_state_id=to_state_id
        ).first()
        if not transition:
            return Response({"error": "Transition is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        if transition.requires_approval:
            approval = WorkflowApproval.objects.create(
                workspace_id=issue.workspace_id,
                project_id=project_id,
                issue=issue,
                transition=transition,
                requested_by=request.user,
            )
            return Response(WorkflowApprovalSerializer(approval).data, status=status.HTTP_202_ACCEPTED)
        issue.state_id = to_state_id
        issue.save(update_fields=["state"])
        return Response({"id": str(issue.id), "state": str(issue.state_id)})


class WorkflowApprovalEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN])
    def post(self, request, slug, project_id, pk):
        approval = WorkflowApproval.objects.get(workspace__slug=slug, project_id=project_id, pk=pk)
        decision = request.data.get("status", "approved")
        approval.status = decision
        approval.decided_by = request.user
        approval.comment = request.data.get("comment", "")
        approval.save()
        if decision == "approved":
            issue = approval.issue
            issue.state_id = approval.transition.to_state_id
            issue.save(update_fields=["state"])
        return Response(WorkflowApprovalSerializer(approval).data)


class WorkItemTemplateViewSet(BaseViewSet):
    serializer_class = WorkItemTemplateSerializer
    model = WorkItemTemplate

    def get_queryset(self):
        return WorkItemTemplate.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def retrieve(self, request, slug, project_id, pk):
        return Response(self.get_serializer(self.get_queryset().get(pk=pk)).data)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApplyWorkItemTemplateEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, pk):
        template = WorkItemTemplate.objects.get(workspace__slug=slug, project_id=project_id, pk=pk)
        payload = dict(template.payload or {})
        payload.pop("id", None)
        issue = Issue.objects.create(project_id=project_id, name=payload.get("name") or template.name, **{
            k: v for k, v in payload.items() if k in {"priority", "description_html"} and v is not None
        })
        if payload.get("type"):
            issue.type_id = payload["type"]
            issue.save(update_fields=["type"])
        return Response({"id": str(issue.id), "name": issue.name}, status=status.HTTP_201_CREATED)


class ProjectTemplateViewSet(BaseViewSet):
    serializer_class = ProjectTemplateSerializer
    model = ProjectTemplate

    def get_queryset(self):
        return ProjectTemplate.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecurringIssueViewSet(BaseViewSet):
    serializer_class = RecurringIssueSerializer
    model = RecurringIssue

    def get_queryset(self):
        return RecurringIssue.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerViewSet(BaseViewSet):
    serializer_class = CustomerSerializer
    model = Customer

    def get_queryset(self):
        return Customer.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def partial_update(self, request, slug, pk):
        obj = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerIssueViewSet(BaseViewSet):
    serializer_class = CustomerIssueSerializer
    model = CustomerIssue

    def get_queryset(self):
        return CustomerIssue.objects.filter(workspace__slug=self.kwargs["slug"], customer_id=self.kwargs["customer_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def list(self, request, slug, customer_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def create(self, request, slug, customer_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, customer_id=customer_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomRoleViewSet(BaseViewSet):
    serializer_class = CustomRoleSerializer
    model = CustomRole

    def get_queryset(self):
        return CustomRole.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccessRuleViewSet(BaseViewSet):
    serializer_class = AccessRuleSerializer
    model = AccessRule

    def get_queryset(self):
        return AccessRule.objects.filter(workspace__slug=self.kwargs["slug"], role_id=self.kwargs["role_id"])

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def list(self, request, slug, role_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug, role_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, role_id=role_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, role_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleAssignmentViewSet(BaseViewSet):
    serializer_class = RoleAssignmentSerializer
    model = RoleAssignment

    def get_queryset(self):
        return RoleAssignment.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save(workspace=workspace)
        if assignment.project_id:
            from plane.db.models import ProjectMember

            ProjectMember.objects.filter(project_id=assignment.project_id, member_id=assignment.member_id).update(
                role=assignment.role.level
            )
        else:
            WorkspaceMember.objects.filter(workspace=workspace, member_id=assignment.member_id).update(
                role=assignment.role.level
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuditLogViewSet(BaseViewSet):
    serializer_class = AuditLogSerializer
    model = AuditLog

    def get_queryset(self):
        return AuditLog.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset()[:200], many=True).data)


class SLAPolicyViewSet(BaseViewSet):
    serializer_class = SLAPolicySerializer
    model = SLAPolicy

    def get_queryset(self):
        return SLAPolicy.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, project_id=project_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IntakeSLAEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def get(self, request, slug, project_id):
        policy = SLAPolicy.objects.filter(workspace__slug=slug, project_id=project_id, is_default=True).first()
        items = IntakeIssue.objects.filter(workspace__slug=slug, project_id=project_id, status=-2)
        now = timezone.now()
        rows = []
        for item in items:
            age = (now - item.created_at).total_seconds() / 60
            rows.append(
                {
                    "id": str(item.id),
                    "issue": str(item.issue_id),
                    "age_minutes": age,
                    "breached_first_response": bool(policy and age > policy.first_response_minutes),
                    "breached_resolution": bool(policy and age > policy.resolution_minutes),
                }
            )
        return Response(rows)


class IntakeFormViewSet(BaseViewSet):
    serializer_class = IntakeFormSerializer
    model = IntakeForm

    def get_queryset(self):
        return IntakeForm.objects.filter(workspace__slug=self.kwargs["slug"], project_id=self.kwargs["project_id"])

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        workspace = Workspace.objects.get(slug=slug)
        intake = Intake.objects.filter(project_id=project_id).first()
        if not intake:
            return Response({"error": "Project has no intake"}, status=status.HTTP_400_BAD_REQUEST)
        name = request.data.get("name", "Intake form")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            workspace=workspace,
            project_id=project_id,
            intake=intake,
            slug=request.data.get("slug") or f"{slugify(name)}-{uuid4().hex[:8]}",
            inbound_email=request.data.get("inbound_email") or f"intake-{uuid4().hex[:8]}@forms.local",
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicIntakeFormEndpoint(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, form_slug):
        form = IntakeForm.objects.filter(slug=form_slug, is_active=True).first()
        if not form:
            return Response({"error": "Form not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"name": form.name, "description": form.description, "fields": form.fields, "slug": form.slug})

    def post(self, request, form_slug):
        form = IntakeForm.objects.filter(slug=form_slug, is_active=True).first()
        if not form:
            return Response({"error": "Form not found"}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get("name") or request.data.get("title") or "Intake submission"
        issue = Issue.objects.create(project_id=form.project_id, name=name, description_html=request.data.get("description") or "")
        IntakeIssue.objects.create(
            workspace_id=form.workspace_id,
            project_id=form.project_id,
            intake=form.intake,
            issue=issue,
            source="FORM",
            source_email=request.data.get("email", ""),
            extra=request.data,
        )
        return Response({"id": str(issue.id)}, status=status.HTTP_201_CREATED)


class IntakeEmailEndpoint(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        inbound = request.data.get("to") or request.data.get("recipient")
        form = IntakeForm.objects.filter(inbound_email=inbound, is_active=True).first()
        if not form:
            return Response({"error": "Unknown intake address"}, status=status.HTTP_404_NOT_FOUND)
        issue = Issue.objects.create(
            project_id=form.project_id,
            name=request.data.get("subject") or "Email intake",
            description_html=request.data.get("body") or "",
        )
        IntakeIssue.objects.create(
            workspace_id=form.workspace_id,
            project_id=form.project_id,
            intake=form.intake,
            issue=issue,
            source="EMAIL",
            source_email=request.data.get("from", ""),
            extra=request.data,
        )
        return Response({"id": str(issue.id)}, status=status.HTTP_201_CREATED)


class SCIMTokenViewSet(BaseViewSet):
    serializer_class = SCIMTokenSerializer
    model = SCIMToken

    def get_queryset(self):
        return SCIMToken.objects.filter(workspace__slug=self.kwargs["slug"])

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def list(self, request, slug):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        token = f"scim_{uuid4().hex}"
        obj = SCIMToken.objects.create(workspace=workspace, name=request.data.get("name", "SCIM"), token=token)
        payload = self.get_serializer(obj).data
        payload["token"] = token
        return Response(payload, status=status.HTTP_201_CREATED)

    @allow_permission([ROLE.ADMIN], level="WORKSPACE")
    def destroy(self, request, slug, pk):
        self.get_queryset().get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SCIMUsersEndpoint(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def _workspace(self, request):
        header = request.headers.get("Authorization", "")
        raw = header.replace("Bearer ", "").strip()
        token = SCIMToken.objects.filter(token=raw, is_active=True).select_related("workspace").first()
        return token.workspace if token else None

    def get(self, request):
        workspace = self._workspace(request)
        if not workspace:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        members = WorkspaceMember.objects.filter(workspace=workspace, is_active=True).select_related("member")
        resources = [
            {
                "id": str(m.member_id),
                "userName": m.member.email,
                "active": True,
                "name": {"givenName": m.member.first_name, "familyName": m.member.last_name},
            }
            for m in members
        ]
        return Response({"schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"], "totalResults": len(resources), "Resources": resources})

    def post(self, request):
        workspace = self._workspace(request)
        if not workspace:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        from plane.db.models import User

        email = (request.data.get("userName") or "").lower()
        name = request.data.get("name") or {}
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"first_name": name.get("givenName", ""), "last_name": name.get("familyName", "")},
        )
        WorkspaceMember.objects.get_or_create(workspace=workspace, member=user, defaults={"role": 15, "is_active": True})
        return Response({"id": str(user.id), "userName": user.email}, status=status.HTTP_201_CREATED)


class PropertyRollupEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def get(self, request, slug):
        definitions = CustomProperty.objects.filter(workspace__slug=slug, is_workspace_level=True)
        rows = []
        for definition in definitions:
            values = CustomPropertyValue.objects.filter(definition=definition)
            rows.append({"id": str(definition.id), "name": definition.name, "count": values.count()})
        return Response(rows)
