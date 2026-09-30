# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from plane.app.serializers.base import BaseSerializer
from plane.db.models import IssueType, ProjectIssueType
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


class IssueTypeSerializer(BaseSerializer):
    class Meta:
        model = IssueType
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class ProjectIssueTypeSerializer(BaseSerializer):
    class Meta:
        model = ProjectIssueType
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class CustomPropertySerializer(BaseSerializer):
    class Meta:
        model = CustomProperty
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class CustomPropertyValueSerializer(BaseSerializer):
    class Meta:
        model = CustomPropertyValue
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class WorklogSerializer(BaseSerializer):
    class Meta:
        model = Worklog
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class WorklogTimerSerializer(BaseSerializer):
    class Meta:
        model = WorklogTimer
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class TeamspaceSerializer(BaseSerializer):
    class Meta:
        model = Teamspace
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class TeamspaceMemberSerializer(BaseSerializer):
    class Meta:
        model = TeamspaceMember
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class TeamspaceProjectSerializer(BaseSerializer):
    class Meta:
        model = TeamspaceProject
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class InitiativeSerializer(BaseSerializer):
    class Meta:
        model = Initiative
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class InitiativeProjectSerializer(BaseSerializer):
    class Meta:
        model = InitiativeProject
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class InitiativeIssueSerializer(BaseSerializer):
    class Meta:
        model = InitiativeIssue
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class DashboardSerializer(BaseSerializer):
    class Meta:
        model = Dashboard
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class DashboardWidgetSerializer(BaseSerializer):
    class Meta:
        model = DashboardWidget
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class WorkflowSerializer(BaseSerializer):
    class Meta:
        model = Workflow
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class WorkflowTransitionSerializer(BaseSerializer):
    class Meta:
        model = WorkflowTransition
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class WorkflowApprovalSerializer(BaseSerializer):
    class Meta:
        model = WorkflowApproval
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class WorkItemTemplateSerializer(BaseSerializer):
    class Meta:
        model = WorkItemTemplate
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class ProjectTemplateSerializer(BaseSerializer):
    class Meta:
        model = ProjectTemplate
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class RecurringIssueSerializer(BaseSerializer):
    class Meta:
        model = RecurringIssue
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class CustomerSerializer(BaseSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class CustomerIssueSerializer(BaseSerializer):
    class Meta:
        model = CustomerIssue
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class CustomRoleSerializer(BaseSerializer):
    class Meta:
        model = CustomRole
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class AccessRuleSerializer(BaseSerializer):
    class Meta:
        model = AccessRule
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class RoleAssignmentSerializer(BaseSerializer):
    class Meta:
        model = RoleAssignment
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class AuditLogSerializer(BaseSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ["workspace", "created_by", "updated_by"]


class SLAPolicySerializer(BaseSerializer):
    class Meta:
        model = SLAPolicy
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class IntakeFormSerializer(BaseSerializer):
    class Meta:
        model = IntakeForm
        fields = "__all__"
        read_only_fields = ["workspace", "project", "created_by", "updated_by"]


class SCIMTokenSerializer(BaseSerializer):
    class Meta:
        model = SCIMToken
        fields = "__all__"
        read_only_fields = ["workspace", "token", "created_by", "updated_by"]
