import pytest

from app.rbac.acl import DOC_CLASS_ACL, Role, acl_for, build_acl_filter


def test_exactly_30_entries():
    assert len(DOC_CLASS_ACL) == 30


def test_c_level_in_every_row():
    for doc_class, entry in DOC_CLASS_ACL.items():
        assert Role.C_LEVEL in entry["roles"], f"{doc_class} is missing c_level"


def test_no_employee_on_confidential_or_restricted():
    for doc_class, entry in DOC_CLASS_ACL.items():
        if entry["sensitivity"] in ("confidential", "restricted"):
            assert Role.EMPLOYEE not in entry["roles"], f"{doc_class} wrongly grants employee access"


def test_cloud_costs_overlap():
    roles, sensitivity = acl_for("cloud_costs")
    assert set(roles) == {"finance_analyst", "engineering_lead", "c_level"}
    assert sensitivity == "confidential"


def test_marketing_spend_overlap():
    roles, sensitivity = acl_for("marketing_spend")
    assert set(roles) == {"finance_analyst", "sales_lead", "c_level"}
    assert sensitivity == "confidential"


def test_unknown_doc_class_defaults_to_c_level_restricted():
    roles, sensitivity = acl_for("typo_class")
    assert roles == ["c_level"]
    assert sensitivity == "restricted"


def test_build_acl_filter_raises_on_empty_roles():
    with pytest.raises(ValueError):
        build_acl_filter([])
