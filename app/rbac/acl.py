from __future__ import annotations
from enum import StrEnum
from qdrant_client import models


class Role(StrEnum):
    EMPLOYEE = "employee"
    HR_MANAGER = "hr_manager"
    FINANCE_ANALYST = "finance_analyst"
    SALES_LEAD = "sales_lead"
    ENGINEERING_LEAD = "engineering_lead"
    C_LEVEL = "c_level"


class Sensitivity(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


_SENSITIVITY_ORDER = [Sensitivity.PUBLIC, Sensitivity.INTERNAL, Sensitivity.CONFIDENTIAL, Sensitivity.RESTRICTED]
ALL_ROLES = [r for r in Role]

DOC_CLASS_ACL: dict[str, dict] = {
    "handbook":             {"sensitivity": Sensitivity.PUBLIC,       "roles": ALL_ROLES},
    "holiday_calendar":     {"sensitivity": Sensitivity.PUBLIC,       "roles": ALL_ROLES},
    "it_howto":             {"sensitivity": Sensitivity.PUBLIC,       "roles": ALL_ROLES},
    "org_chart":            {"sensitivity": Sensitivity.INTERNAL,     "roles": ALL_ROLES},
    "all_hands_notes":      {"sensitivity": Sensitivity.INTERNAL,     "roles": ALL_ROLES},
    "product_roadmap":      {"sensitivity": Sensitivity.INTERNAL,     "roles": ALL_ROLES},
    "expense_policy":       {"sensitivity": Sensitivity.INTERNAL,     "roles": ALL_ROLES},

    "employee_records":     {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.HR_MANAGER, Role.C_LEVEL]},
    "payroll":               {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.HR_MANAGER, Role.C_LEVEL]},
    "performance_review":   {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.HR_MANAGER, Role.C_LEVEL]},
    "hiring_pipeline":      {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.HR_MANAGER, Role.C_LEVEL]},
    "comp_bands":           {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.HR_MANAGER, Role.C_LEVEL]},

    "quarterly_financials": {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.FINANCE_ANALYST, Role.C_LEVEL]},
    "budget":                {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.FINANCE_ANALYST, Role.C_LEVEL]},
    "vendor_contract":      {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.FINANCE_ANALYST, Role.C_LEVEL]},
    "invoice":               {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.FINANCE_ANALYST, Role.C_LEVEL]},

    # overlap case: finance AND sales both need this
    "marketing_spend":      {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.FINANCE_ANALYST, Role.SALES_LEAD, Role.C_LEVEL]},
    "marketing_strategy":   {"sensitivity": Sensitivity.INTERNAL,     "roles": [Role.SALES_LEAD, Role.C_LEVEL]},
    "sales_pipeline":       {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.SALES_LEAD, Role.C_LEVEL]},
    "customer_account":     {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.SALES_LEAD, Role.C_LEVEL]},
    "quota_sheet":          {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.SALES_LEAD, Role.C_LEVEL]},

    "architecture_doc":     {"sensitivity": Sensitivity.INTERNAL,     "roles": [Role.ENGINEERING_LEAD, Role.C_LEVEL]},
    "runbook":               {"sensitivity": Sensitivity.INTERNAL,     "roles": [Role.ENGINEERING_LEAD, Role.C_LEVEL]},
    "postmortem":           {"sensitivity": Sensitivity.INTERNAL,     "roles": [Role.ENGINEERING_LEAD, Role.C_LEVEL]},
    "security_review":      {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.ENGINEERING_LEAD, Role.C_LEVEL]},

    # overlap case: finance AND engineering both need this
    "cloud_costs":          {"sensitivity": Sensitivity.CONFIDENTIAL, "roles": [Role.FINANCE_ANALYST, Role.ENGINEERING_LEAD, Role.C_LEVEL]},

    "board_deck":           {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.C_LEVEL]},
    "strategy_memo":        {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.C_LEVEL]},
    "ma_exploration":       {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.C_LEVEL]},
    "restructuring_plan":   {"sensitivity": Sensitivity.RESTRICTED,   "roles": [Role.C_LEVEL]},
}


def acl_for(doc_class: str) -> tuple[list[str], str]:
    entry = DOC_CLASS_ACL.get(doc_class)
    if entry is None:
        return ([Role.C_LEVEL.value], Sensitivity.RESTRICTED.value)
    return ([str(r) for r in entry["roles"]], str(entry["sensitivity"]))


def most_restrictive(sensitivities: list[str]) -> str:
    return str(max(sensitivities, key=lambda s: _SENSITIVITY_ORDER.index(Sensitivity(s))))


def build_acl_filter(user_roles: list[str]) -> models.Filter:
    if not user_roles:
        raise ValueError("refusing to build an ACL filter with no roles")
    return models.Filter(
        must=[models.FieldCondition(key="allowed_roles", match=models.MatchAny(any=list(user_roles)))]
    )