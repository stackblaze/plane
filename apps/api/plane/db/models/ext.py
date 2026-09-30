# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.conf import settings
from django.db import models

from .base import BaseModel
from .project import ProjectBaseModel
from .workspace import WorkspaceBaseModel


class CustomProperty(WorkspaceBaseModel):
    TYPE_CHOICES = (
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("select", "Select"),
        ("multi_select", "Multi select"),
        ("boolean", "Boolean"),
        ("url", "URL"),
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    property_type = models.CharField(max_length=32, choices=TYPE_CHOICES, default="text")
    options = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=False)
    is_workspace_level = models.BooleanField(default=False)
    sort_order = models.FloatField(default=65535)
    issue_type = models.ForeignKey(
        "db.IssueType", on_delete=models.SET_NULL, null=True, blank=True, related_name="custom_properties"
    )

    class Meta:
        db_table = "ext_custom_properties"
        ordering = ("sort_order", "name")


class CustomPropertyValue(ProjectBaseModel):
    definition = models.ForeignKey(CustomProperty, on_delete=models.CASCADE, related_name="values")
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="custom_property_values")
    value = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ext_custom_property_values"
        unique_together = ["definition", "issue", "deleted_at"]


class Worklog(ProjectBaseModel):
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="worklogs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worklogs")
    duration_minutes = models.PositiveIntegerField(default=0)
    logged_on = models.DateField()
    description = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ext_worklogs"
        ordering = ("-logged_on", "-created_at")


class WorklogTimer(ProjectBaseModel):
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="worklog_timers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worklog_timers")
    started_at = models.DateTimeField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = "ext_worklog_timers"
        unique_together = ["issue", "user", "deleted_at"]


class Teamspace(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo_props = models.JSONField(default=dict)
    is_private = models.BooleanField(default=False)

    class Meta:
        db_table = "ext_teamspaces"
        ordering = ("name",)


class TeamspaceMember(WorkspaceBaseModel):
    teamspace = models.ForeignKey(Teamspace, on_delete=models.CASCADE, related_name="members")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teamspace_memberships")
    role = models.PositiveIntegerField(default=15)

    class Meta:
        db_table = "ext_teamspace_members"
        unique_together = ["teamspace", "member", "deleted_at"]


class TeamspaceProject(WorkspaceBaseModel):
    teamspace = models.ForeignKey(Teamspace, on_delete=models.CASCADE, related_name="projects")

    class Meta:
        db_table = "ext_teamspace_projects"
        unique_together = ["teamspace", "project", "deleted_at"]


class Initiative(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo_props = models.JSONField(default=dict)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_initiatives"
    )
    status = models.CharField(max_length=32, default="planned")

    class Meta:
        db_table = "ext_initiatives"
        ordering = ("-created_at",)


class InitiativeProject(WorkspaceBaseModel):
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name="projects")

    class Meta:
        db_table = "ext_initiative_projects"
        unique_together = ["initiative", "project", "deleted_at"]


class InitiativeIssue(WorkspaceBaseModel):
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name="issues")
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="initiatives")

    class Meta:
        db_table = "ext_initiative_issues"
        unique_together = ["initiative", "issue", "deleted_at"]


class Dashboard(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    layout = models.JSONField(default=dict)

    class Meta:
        db_table = "ext_dashboards"
        ordering = ("name",)


class DashboardWidget(WorkspaceBaseModel):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="widgets")
    widget_type = models.CharField(max_length=64)
    title = models.CharField(max_length=255, blank=True)
    config = models.JSONField(default=dict)
    sort_order = models.FloatField(default=65535)

    class Meta:
        db_table = "ext_dashboard_widgets"
        ordering = ("sort_order",)


class Workflow(ProjectBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    issue_type = models.ForeignKey(
        "db.IssueType", on_delete=models.SET_NULL, null=True, blank=True, related_name="workflows"
    )

    class Meta:
        db_table = "ext_workflows"
        ordering = ("name",)


class WorkflowTransition(ProjectBaseModel):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="transitions")
    from_state = models.ForeignKey("db.State", on_delete=models.CASCADE, related_name="workflow_from")
    to_state = models.ForeignKey("db.State", on_delete=models.CASCADE, related_name="workflow_to")
    requires_approval = models.BooleanField(default=False)
    approver_role = models.PositiveIntegerField(default=20)

    class Meta:
        db_table = "ext_workflow_transitions"
        unique_together = ["workflow", "from_state", "to_state", "deleted_at"]


class WorkflowApproval(ProjectBaseModel):
    STATUS_CHOICES = (("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"))
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="workflow_approvals")
    transition = models.ForeignKey(WorkflowTransition, on_delete=models.CASCADE, related_name="approvals")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_approvals"
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="decided_approvals"
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "ext_workflow_approvals"
        ordering = ("-created_at",)


class WorkItemTemplate(ProjectBaseModel):
    name = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "ext_work_item_templates"
        ordering = ("name",)


class ProjectTemplate(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "ext_project_templates"
        ordering = ("name",)


class RecurringIssue(ProjectBaseModel):
    template = models.ForeignKey(WorkItemTemplate, on_delete=models.CASCADE, related_name="schedules")
    cadence = models.CharField(max_length=32, default="weekly")
    next_run_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ext_recurring_issues"
        ordering = ("next_run_at",)


class Customer(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    domain = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "ext_customers"
        ordering = ("name",)


class CustomerIssue(WorkspaceBaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="issues")
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="customers")

    class Meta:
        db_table = "ext_customer_issues"
        unique_together = ["customer", "issue", "deleted_at"]


class CustomRole(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    level = models.PositiveIntegerField(default=15)
    permissions = models.JSONField(default=dict)

    class Meta:
        db_table = "ext_custom_roles"
        ordering = ("-level", "name")


class AccessRule(WorkspaceBaseModel):
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE, related_name="access_rules")
    resource = models.CharField(max_length=64)
    field = models.CharField(max_length=64, blank=True)
    action = models.CharField(max_length=32, default="read")
    effect = models.CharField(max_length=16, default="allow")

    class Meta:
        db_table = "ext_access_rules"


class AuditLog(WorkspaceBaseModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=512)
    status_code = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    body = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ext_audit_logs"
        ordering = ("-created_at",)


class SLAPolicy(ProjectBaseModel):
    name = models.CharField(max_length=255)
    first_response_minutes = models.PositiveIntegerField(default=60)
    resolution_minutes = models.PositiveIntegerField(default=1440)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "ext_sla_policies"
        ordering = ("name",)


class IntakeForm(ProjectBaseModel):
    intake = models.ForeignKey("db.Intake", on_delete=models.CASCADE, related_name="forms")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fields = models.JSONField(default=list)
    slug = models.SlugField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    inbound_email = models.EmailField(blank=True)

    class Meta:
        db_table = "ext_intake_forms"
        ordering = ("name",)


class SCIMToken(WorkspaceBaseModel):
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "ext_scim_tokens"


class RoleAssignment(WorkspaceBaseModel):
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE, related_name="assignments")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="custom_role_assignments")

    class Meta:
        db_table = "ext_role_assignments"
