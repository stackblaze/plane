# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.app.views.ext import (
    AccessRuleViewSet,
    ApplyWorkItemTemplateEndpoint,
    AuditLogViewSet,
    CustomPropertyValueViewSet,
    CustomPropertyViewSet,
    CustomRoleViewSet,
    CustomerIssueViewSet,
    CustomerViewSet,
    DashboardViewSet,
    DashboardWidgetViewSet,
    ExtCycleProgressEndpoint,
    InitiativeLinkEndpoint,
    InitiativeViewSet,
    IntakeEmailEndpoint,
    IntakeFormViewSet,
    IntakeSLAEndpoint,
    IssueTypeAssignEndpoint,
    IssueTypeViewSet,
    IssueWorkflowTransitionEndpoint,
    ProjectIssueTypeViewSet,
    ProjectTemplateViewSet,
    PropertyRollupEndpoint,
    PublicIntakeFormEndpoint,
    PublishEntityEndpoint,
    RecurringIssueViewSet,
    RoleAssignmentViewSet,
    SCIMTokenViewSet,
    SCIMUsersEndpoint,
    SLAPolicyViewSet,
    TeamspaceMemberViewSet,
    TeamspaceProjectViewSet,
    TeamspaceViewSet,
    WikiPageViewSet,
    WorkItemTemplateViewSet,
    WorkflowApprovalEndpoint,
    WorkflowTransitionViewSet,
    WorkflowViewSet,
    WorklogReportEndpoint,
    WorklogTimerEndpoint,
    WorklogViewSet,
)

urlpatterns = [
    path("workspaces/<str:slug>/issue-types/", IssueTypeViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/issue-types/<uuid:pk>/",
        IssueTypeViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issue-types/",
        ProjectIssueTypeViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issue-types/<uuid:pk>/",
        ProjectIssueTypeViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issues/<uuid:issue_id>/type/",
        IssueTypeAssignEndpoint.as_view(),
    ),
    path("workspaces/<str:slug>/custom-properties/", CustomPropertyViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/custom-properties/<uuid:pk>/",
        CustomPropertyViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/custom-properties/",
        CustomPropertyViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issues/<uuid:issue_id>/custom-properties/",
        CustomPropertyValueViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issues/<uuid:issue_id>/worklogs/",
        WorklogViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issues/<uuid:issue_id>/worklogs/<uuid:pk>/",
        WorklogViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issues/<uuid:issue_id>/timer/",
        WorklogTimerEndpoint.as_view(),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/worklog-report/",
        WorklogReportEndpoint.as_view(),
    ),
    path("workspaces/<str:slug>/teamspaces/", TeamspaceViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/teamspaces/<uuid:pk>/",
        TeamspaceViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/teamspaces/<uuid:teamspace_id>/members/",
        TeamspaceMemberViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/teamspaces/<uuid:teamspace_id>/members/<uuid:pk>/",
        TeamspaceMemberViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/teamspaces/<uuid:teamspace_id>/projects/",
        TeamspaceProjectViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/teamspaces/<uuid:teamspace_id>/projects/<uuid:pk>/",
        TeamspaceProjectViewSet.as_view({"delete": "destroy"}),
    ),
    path("workspaces/<str:slug>/initiatives/", InitiativeViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/initiatives/<uuid:pk>/",
        InitiativeViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
    ),
    path("workspaces/<str:slug>/initiatives/<uuid:pk>/links/", InitiativeLinkEndpoint.as_view()),
    path("workspaces/<str:slug>/dashboards/", DashboardViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/dashboards/<uuid:pk>/",
        DashboardViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/dashboards/<uuid:dashboard_id>/widgets/",
        DashboardWidgetViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/dashboards/<uuid:dashboard_id>/widgets/<uuid:pk>/",
        DashboardWidgetViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/cycle-progress/",
        ExtCycleProgressEndpoint.as_view(),
    ),
    path("workspaces/<str:slug>/wiki/", WikiPageViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/publish/",
        PublishEntityEndpoint.as_view(),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/workflows/",
        WorkflowViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/workflows/<uuid:pk>/",
        WorkflowViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/workflows/<uuid:workflow_id>/transitions/",
        WorkflowTransitionViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/workflows/<uuid:workflow_id>/transitions/<uuid:pk>/",
        WorkflowTransitionViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issues/<uuid:issue_id>/workflow-transition/",
        IssueWorkflowTransitionEndpoint.as_view(),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/workflow-approvals/<uuid:pk>/",
        WorkflowApprovalEndpoint.as_view(),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/work-item-templates/",
        WorkItemTemplateViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/work-item-templates/<uuid:pk>/",
        WorkItemTemplateViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/work-item-templates/<uuid:pk>/apply/",
        ApplyWorkItemTemplateEndpoint.as_view(),
    ),
    path(
        "workspaces/<str:slug>/project-templates/",
        ProjectTemplateViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/project-templates/<uuid:pk>/",
        ProjectTemplateViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/recurring-issues/",
        RecurringIssueViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/recurring-issues/<uuid:pk>/",
        RecurringIssueViewSet.as_view({"delete": "destroy"}),
    ),
    path("workspaces/<str:slug>/customers/", CustomerViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "workspaces/<str:slug>/customers/<uuid:pk>/",
        CustomerViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/issues/",
        CustomerIssueViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path("workspaces/<str:slug>/roles/", CustomRoleViewSet.as_view({"get": "list", "post": "create"})),
    path("workspaces/<str:slug>/roles/<uuid:pk>/", CustomRoleViewSet.as_view({"delete": "destroy"})),
    path(
        "workspaces/<str:slug>/roles/<uuid:role_id>/rules/",
        AccessRuleViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/roles/<uuid:role_id>/rules/<uuid:pk>/",
        AccessRuleViewSet.as_view({"delete": "destroy"}),
    ),
    path("workspaces/<str:slug>/role-assignments/", RoleAssignmentViewSet.as_view({"get": "list", "post": "create"})),
    path("workspaces/<str:slug>/audit-logs/", AuditLogViewSet.as_view({"get": "list"})),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/slas/",
        SLAPolicyViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/slas/<uuid:pk>/",
        SLAPolicyViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/intake-sla/",
        IntakeSLAEndpoint.as_view(),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/intake-forms/",
        IntakeFormViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/intake-forms/<uuid:pk>/",
        IntakeFormViewSet.as_view({"delete": "destroy"}),
    ),
    path("intake-forms/<slug:form_slug>/", PublicIntakeFormEndpoint.as_view()),
    path("intake-email/", IntakeEmailEndpoint.as_view()),
    path("workspaces/<str:slug>/scim-tokens/", SCIMTokenViewSet.as_view({"get": "list", "post": "create"})),
    path("workspaces/<str:slug>/scim-tokens/<uuid:pk>/", SCIMTokenViewSet.as_view({"delete": "destroy"})),
    path("scim/v2/Users", SCIMUsersEndpoint.as_view()),
    path("workspaces/<str:slug>/property-rollups/", PropertyRollupEndpoint.as_view()),
]
