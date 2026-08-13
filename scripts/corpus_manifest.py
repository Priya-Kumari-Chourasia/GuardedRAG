"""
The plan for all 100 synthetic documents, before any AI-generated content exists.

Each entry says: what to call it, which ACL doc_class it belongs to (must match a key
in app/rbac/acl.py's DOC_CLASS_ACL exactly), which department "owns" it, whether it
should contain fake PII, and whether it's one of our five deliberately planted test cases.

scripts/generate_corpus.py will loop over this list and ask the AI to write the actual
body text for each entry.
"""

MANIFEST = [
    # ---- company-wide (15) --------------------------------------------------
    {"doc_id": "co-handbook-2026", "doc_class": "handbook", "department": "company_wide", "title": "PKC Employee Handbook 2026"},
    {"doc_id": "co-holiday-calendar-2026", "doc_class": "holiday_calendar", "department": "company_wide", "title": "PKC Holiday Calendar 2026"},
    {"doc_id": "co-it-howto-equipment", "doc_class": "it_howto", "department": "company_wide", "title": "IT How-To: Requesting New Equipment"},
    {"doc_id": "co-it-howto-vpn", "doc_class": "it_howto", "department": "company_wide", "title": "IT How-To: VPN Setup Guide"},
    {"doc_id": "co-it-howto-password", "doc_class": "it_howto", "department": "company_wide", "title": "IT How-To: Resetting Your Password"},
    {"doc_id": "co-it-howto-slack-email", "doc_class": "it_howto", "department": "company_wide", "title": "IT How-To: Setting Up Slack and Email"},
    {"doc_id": "co-org-chart-q3-2025", "doc_class": "org_chart", "department": "company_wide", "title": "PKC Organization Chart — Q3 2025"},
    {"doc_id": "co-allhands-2025-06", "doc_class": "all_hands_notes", "department": "company_wide", "title": "All-Hands Notes — June 2025"},
    {"doc_id": "co-allhands-2025-07", "doc_class": "all_hands_notes", "department": "company_wide", "title": "All-Hands Notes — July 2025"},
    {"doc_id": "co-allhands-2025-09", "doc_class": "all_hands_notes", "department": "company_wide", "title": "Company Update: Strategic Announcement (All-Hands Summary)", "special_case": "near_dup_public"},
    {"doc_id": "co-roadmap-h2-2025", "doc_class": "product_roadmap", "department": "company_wide", "title": "Product Roadmap H2 2025"},
    {"doc_id": "co-roadmap-h1-2026", "doc_class": "product_roadmap", "department": "company_wide", "title": "Product Roadmap H1 2026"},
    {"doc_id": "co-expense-policy", "doc_class": "expense_policy", "department": "company_wide", "title": "Employee Expense Reimbursement Policy"},
    {"doc_id": "co-remote-work-addendum", "doc_class": "handbook", "department": "company_wide", "title": "Remote Work Policy Addendum"},
    {"doc_id": "co-office-closure-diwali", "doc_class": "holiday_calendar", "department": "company_wide", "title": "Office Closure Notice — Diwali 2025"},

    # ---- HR (20) --------------------------------------------------------------
    {"doc_id": "hr-emp-record-ravi", "doc_class": "employee_records", "department": "hr", "title": "Employee Record — Ravi Kumar", "contains_pii": True},
    {"doc_id": "hr-emp-record-neha", "doc_class": "employee_records", "department": "hr", "title": "Employee Record — Neha Gupta", "contains_pii": True},
    {"doc_id": "hr-emp-record-arjun", "doc_class": "employee_records", "department": "hr", "title": "Employee Record — Arjun Rao", "contains_pii": True},
    {"doc_id": "hr-emp-record-divya", "doc_class": "employee_records", "department": "hr", "title": "Employee Record — Divya Menon", "contains_pii": True},
    {"doc_id": "hr-emp-record-karan", "doc_class": "employee_records", "department": "hr", "title": "Employee Record — Karan Malhotra", "contains_pii": True},
    {"doc_id": "hr-emp-record-meera", "doc_class": "employee_records", "department": "hr", "title": "Employee Record — Meera Iyer", "contains_pii": True},
    {"doc_id": "hr-payroll-2025-07", "doc_class": "payroll", "department": "hr", "title": "Payroll Summary — July 2025", "contains_pii": True},
    {"doc_id": "hr-payroll-2025-08", "doc_class": "payroll", "department": "hr", "title": "Payroll Summary — August 2025", "contains_pii": True},
    {"doc_id": "hr-payroll-2025-09", "doc_class": "payroll", "department": "hr", "title": "Payroll Summary — September 2025", "contains_pii": True},
    {"doc_id": "hr-payroll-tax-q3-2025", "doc_class": "payroll", "department": "hr", "title": "Payroll Tax Filing Summary — Q3 2025", "contains_pii": True},
    {"doc_id": "hr-perf-review-karan", "doc_class": "performance_review", "department": "hr", "title": "Performance Review — Karan Malhotra, Q2 2025", "contains_pii": True},
    {"doc_id": "hr-perf-review-ravi", "doc_class": "performance_review", "department": "hr", "title": "Performance Review — Ravi Kumar, Q2 2025", "contains_pii": True},
    {"doc_id": "hr-perf-review-neha", "doc_class": "performance_review", "department": "hr", "title": "Performance Review — Neha Gupta, Q2 2025", "contains_pii": True},
    {"doc_id": "hr-hiring-backend-eng", "doc_class": "hiring_pipeline", "department": "hr", "title": "Hiring Pipeline — Senior Backend Engineer"},
    {"doc_id": "hr-hiring-designer", "doc_class": "hiring_pipeline", "department": "hr", "title": "Hiring Pipeline — Product Designer"},
    {"doc_id": "hr-hiring-sdr", "doc_class": "hiring_pipeline", "department": "hr", "title": "Hiring Pipeline — Sales Development Rep"},
    {"doc_id": "hr-hiring-finance-analyst", "doc_class": "hiring_pipeline", "department": "hr", "title": "Hiring Pipeline — Finance Analyst"},
    {"doc_id": "hr-comp-bands-eng", "doc_class": "comp_bands", "department": "hr", "title": "Compensation Bands — Engineering"},
    {"doc_id": "hr-comp-bands-sales", "doc_class": "comp_bands", "department": "hr", "title": "Compensation Bands — Sales"},
    {"doc_id": "hr-comp-bands-corp", "doc_class": "comp_bands", "department": "hr", "title": "Compensation Bands — Corporate Functions"},

    # ---- finance (20) -----------------------------------------------------
    {"doc_id": "fin-q1-2025-report", "doc_class": "quarterly_financials", "department": "finance", "title": "Q1 2025 Financial Report"},
    {"doc_id": "fin-q2-2025-report", "doc_class": "quarterly_financials", "department": "finance", "title": "Q2 2025 Financial Report"},
    {"doc_id": "fin-q3-2025-forecast", "doc_class": "quarterly_financials", "department": "finance", "title": "Q3 2025 Financial Report — FORECAST", "special_case": "forecast"},
    {"doc_id": "fin-q3-2025-report", "doc_class": "quarterly_financials", "department": "finance", "title": "Q3 2025 Financial Report — ACTUALS", "special_case": "actuals"},
    {"doc_id": "fin-q4-2025-report", "doc_class": "quarterly_financials", "department": "finance", "title": "Q4 2025 Financial Report"},
    {"doc_id": "fin-annual-summary-2024", "doc_class": "quarterly_financials", "department": "finance", "title": "Annual Financial Summary 2024"},
    {"doc_id": "fin-budget-2025", "doc_class": "budget", "department": "finance", "title": "FY2025 Annual Budget"},
    {"doc_id": "fin-budget-2026-draft", "doc_class": "budget", "department": "finance", "title": "FY2026 Annual Budget Draft"},
    {"doc_id": "fin-budget-eng-2025", "doc_class": "budget", "department": "finance", "title": "Engineering Department Budget 2025"},
    {"doc_id": "fin-budget-sales-2025", "doc_class": "budget", "department": "finance", "title": "Sales Department Budget 2025"},
    {"doc_id": "fin-budget-marketing-2025", "doc_class": "budget", "department": "finance", "title": "Marketing Budget Allocation 2025"},
    {"doc_id": "fin-vendor-aws", "doc_class": "vendor_contract", "department": "finance", "title": "Vendor Contract — AWS Enterprise Agreement", "special_case": "cross_ref"},
    {"doc_id": "fin-vendor-salesforce", "doc_class": "vendor_contract", "department": "finance", "title": "Vendor Contract — Salesforce License Renewal"},
    {"doc_id": "fin-vendor-office-lease", "doc_class": "vendor_contract", "department": "finance", "title": "Vendor Contract — Office Lease Agreement"},
    {"doc_id": "fin-vendor-payroll-service", "doc_class": "vendor_contract", "department": "finance", "title": "Vendor Contract — Payroll Processing Service"},
    {"doc_id": "fin-vendor-groq", "doc_class": "vendor_contract", "department": "finance", "title": "Vendor Contract — Groq Cloud API Services"},
    {"doc_id": "fin-invoice-aws-sep", "doc_class": "invoice", "department": "finance", "title": "Invoice — AWS — September 2025"},
    {"doc_id": "fin-invoice-salesforce-sep", "doc_class": "invoice", "department": "finance", "title": "Invoice — Salesforce — September 2025"},
    {"doc_id": "fin-invoice-office-supplies", "doc_class": "invoice", "department": "finance", "title": "Invoice — Office Supplies Vendor — August 2025"},
    {"doc_id": "fin-invoice-legal-aug", "doc_class": "invoice", "department": "finance", "title": "Invoice — Legal Services — August 2025"},

    # ---- sales & marketing (18) --------------------------------------------
    {"doc_id": "sales-marketing-spend-q3-2025", "doc_class": "marketing_spend", "department": "sales_marketing", "title": "Marketing Spend Report — Q3 2025"},
    {"doc_id": "sales-digital-ad-spend-q3-2025", "doc_class": "marketing_spend", "department": "sales_marketing", "title": "Digital Ad Spend Breakdown — Q3 2025"},
    {"doc_id": "sales-event-sponsorship-2025", "doc_class": "marketing_spend", "department": "sales_marketing", "title": "Event Sponsorship Spend — 2025"},
    {"doc_id": "sales-gtm-strategy-2026", "doc_class": "marketing_strategy", "department": "sales_marketing", "title": "2026 Go-to-Market Strategy"},
    {"doc_id": "sales-launch-campaign-pkc", "doc_class": "marketing_strategy", "department": "sales_marketing", "title": "Product Launch Campaign Plan — PKC Assistant"},
    {"doc_id": "sales-brand-positioning", "doc_class": "marketing_strategy", "department": "sales_marketing", "title": "Brand Positioning Memo"},
    {"doc_id": "sales-competitor-analysis", "doc_class": "marketing_strategy", "department": "sales_marketing", "title": "Competitor Analysis — RAG Assistant Market"},
    {"doc_id": "sales-pipeline-q3-2025", "doc_class": "sales_pipeline", "department": "sales_marketing", "title": "Sales Pipeline Report — Q3 2025"},
    {"doc_id": "sales-pipeline-enterprise-sep", "doc_class": "sales_pipeline", "department": "sales_marketing", "title": "Enterprise Deals Pipeline — September 2025"},
    {"doc_id": "sales-pipeline-renewal-q4", "doc_class": "sales_pipeline", "department": "sales_marketing", "title": "Renewal Pipeline — Q4 2025"},
    {"doc_id": "sales-account-global-retail", "doc_class": "customer_account", "department": "sales_marketing", "title": "Customer Account — Global Retail Corp"},
    {"doc_id": "sales-account-northwind", "doc_class": "customer_account", "department": "sales_marketing", "title": "Customer Account — Northwind Traders"},
    {"doc_id": "sales-account-contoso", "doc_class": "customer_account", "department": "sales_marketing", "title": "Customer Account — Contoso Manufacturing"},
    {"doc_id": "sales-account-meridian", "doc_class": "customer_account", "department": "sales_marketing", "title": "Customer Account — Meridian Logistics"},
    {"doc_id": "sales-account-skyline", "doc_class": "customer_account", "department": "sales_marketing", "title": "Customer Account — Skyline Retailers"},
    {"doc_id": "sales-quota-q3-2025", "doc_class": "quota_sheet", "department": "sales_marketing", "title": "Sales Quota Sheet — Q3 2025"},
    {"doc_id": "sales-quota-q4-2025", "doc_class": "quota_sheet", "department": "sales_marketing", "title": "Sales Quota Sheet — Q4 2025"},
    {"doc_id": "sales-quota-apac", "doc_class": "quota_sheet", "department": "sales_marketing", "title": "Regional Sales Targets — APAC"},

    # ---- engineering (18) --------------------------------------------------
    {"doc_id": "eng-architecture-overview", "doc_class": "architecture_doc", "department": "engineering", "title": "System Architecture Overview — PKC Assistant Platform"},
    {"doc_id": "eng-architecture-rag-pipeline", "doc_class": "architecture_doc", "department": "engineering", "title": "RAG Pipeline Architecture Doc"},
    {"doc_id": "eng-architecture-authz", "doc_class": "architecture_doc", "department": "engineering", "title": "Authentication and Authorization Design"},
    {"doc_id": "eng-architecture-data-pipeline", "doc_class": "architecture_doc", "department": "engineering", "title": "Data Pipeline and Storage Architecture"},
    {"doc_id": "eng-it-tooling-support-system", "doc_class": "architecture_doc", "department": "engineering", "title": "IT Support Ticketing System — Internal Tooling"},
    {"doc_id": "eng-runbook-deploy", "doc_class": "runbook", "department": "engineering", "title": "Runbook — Production Deployment Procedure"},
    {"doc_id": "eng-runbook-incident-response", "doc_class": "runbook", "department": "engineering", "title": "Runbook — Incident Response Checklist"},
    {"doc_id": "eng-runbook-db-backup", "doc_class": "runbook", "department": "engineering", "title": "Runbook — Database Backup and Restore"},
    {"doc_id": "eng-runbook-oncall", "doc_class": "runbook", "department": "engineering", "title": "Runbook — On-Call Escalation Process"},
    {"doc_id": "eng-postmortem-api-outage-sep", "doc_class": "postmortem", "department": "engineering", "title": "Postmortem — September 2025 API Outage"},
    {"doc_id": "eng-postmortem-rate-limit-aug", "doc_class": "postmortem", "department": "engineering", "title": "Postmortem — Rate Limit Incident, August 2025"},
    {"doc_id": "eng-postmortem-embedding-latency", "doc_class": "postmortem", "department": "engineering", "title": "Postmortem — Embedding Service Latency Spike", "special_case": "poisoned"},
    {"doc_id": "eng-security-pentest-q3-2025", "doc_class": "security_review", "department": "engineering", "title": "Security Review — Q3 2025 Penetration Test Summary"},
    {"doc_id": "eng-security-dependency-audit", "doc_class": "security_review", "department": "engineering", "title": "Security Review — Dependency Vulnerability Audit"},
    {"doc_id": "eng-security-access-control-audit", "doc_class": "security_review", "department": "engineering", "title": "Security Review — Access Control Audit"},
    {"doc_id": "eng-cloud-costs-q3-2025", "doc_class": "cloud_costs", "department": "engineering", "title": "Cloud Cost Report — Q3 2025", "special_case": "cross_ref"},
    {"doc_id": "eng-cloud-costs-aws-breakdown-sep", "doc_class": "cloud_costs", "department": "engineering", "title": "AWS Cost Breakdown by Service — September 2025"},
    {"doc_id": "eng-cloud-costs-optimization-q4", "doc_class": "cloud_costs", "department": "engineering", "title": "Cloud Cost Optimization Recommendations — Q4 2025"},

    # ---- executive (9) -------------------------------------------------------
    {"doc_id": "exec-board-deck-q2-2025", "doc_class": "board_deck", "department": "executive", "title": "Board Meeting Deck — Q2 2025"},
    {"doc_id": "exec-board-deck-q3-2025", "doc_class": "board_deck", "department": "executive", "title": "Board Meeting Deck — Q3 2025"},
    {"doc_id": "exec-board-deck-sep-special", "doc_class": "board_deck", "department": "executive", "title": "Board Meeting Deck — September 2025 Special Session", "special_case": "near_dup_restricted"},
    {"doc_id": "exec-strategy-2026-priorities", "doc_class": "strategy_memo", "department": "executive", "title": "2026 Strategic Priorities Memo"},
    {"doc_id": "exec-strategy-competitive-positioning", "doc_class": "strategy_memo", "department": "executive", "title": "Competitive Positioning Memo — Executive Summary"},
    {"doc_id": "exec-ma-acquisition-targets", "doc_class": "ma_exploration", "department": "executive", "title": "M&A Exploration — Potential Acquisition Targets"},
    {"doc_id": "exec-ma-due-diligence-falcon", "doc_class": "ma_exploration", "department": "executive", "title": "Due Diligence Notes — Project Falcon"},
    {"doc_id": "exec-restructuring-eng-division", "doc_class": "restructuring_plan", "department": "executive", "title": "Org Restructuring Plan — Engineering Division"},
    {"doc_id": "exec-restructuring-workforce-2026", "doc_class": "restructuring_plan", "department": "executive", "title": "Workforce Planning — 2026"},
]