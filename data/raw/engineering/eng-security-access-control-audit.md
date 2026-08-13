---
doc_id: eng-security-access-control-audit
doc_class: security_review
department: engineering
title: "Security Review — Access Control Audit"
contains_pii: false
special_case: null
---

# Security Review — Access Control Audit

## 1. Overview  

PKC Technologies (PKC) commissioned an Access Control Audit for the Engineering Division on **12 Mar 2026**. The audit was performed by the internal Security Assurance Team (SAT) led by **Ananya Rao, Sr. Manager – Security Operations**, with support from **Rohit Mehta, Lead IAM Engineer**. The objective was to verify that all privileged access to production systems, source‑code repositories, and CI/CD pipelines complies with PKC’s “Zero‑Trust” policy and to identify any gaps that could expose confidential IP or customer data.

## 2. Scope  

| Asset Category | Systems Covered | Criticality | Review Period |
|----------------|----------------|------------|---------------|
| Cloud Infra (AWS) | EC2, RDS, S3 buckets | High | FY 2025‑26 |
| On‑prem Data‑Center (Bengaluru) | Kubernetes clusters, GitLab EE | High | FY 2025‑26 |
| Development Workstations | 150 laptops (Windows 10/Ubuntu) | Medium | FY 2025‑26 |
| Third‑Party SaaS | Jira, Confluence, Slack | Medium | FY 2025‑26 |

The audit excluded non‑engineering assets (HR, Finance) and focused on **role‑based access control (RBAC)**, **just‑in‑time (JIT) provisioning**, and **audit‑log integrity**.

## 3. Findings  

| # | Finding | Impact | Current Controls | Risk Rating |
|---|---------|--------|------------------|-------------|
| 1 | **Stale privileged accounts** – 12 IAM users with `Admin` rights not used for >90 days (e.g., `devops_temp01`). | Potential misuse if credentials are compromised. | Quarterly review policy exists but not enforced. | High |
| 2 | **Insufficient MFA enforcement** – 28% of engineers accessing production via VPN lack hardware OTP. | Credential theft could lead to lateral movement. | MFA required for AWS console only. | Medium |
| 3 | **Over‑privileged service accounts** – `ci‑runner` service account has `S3FullAccess` though only `ReadOnly` needed. | Data exfiltration risk. | No automated least‑privilege audit. | High |
| 4 | **Audit‑log gaps** – 4 weeks of CloudTrail logs missing due to mis‑configured S3 lifecycle policy (deleted after 30 days). | Loss of forensic evidence. | Log retention policy set to 90 days but not applied. | High |
| 5 | **Unencrypted backup storage** – 3 on‑prem backup volumes stored unencrypted on NAS. | Data breach exposure. | Encryption at rest policy not enforced for legacy backups. | Medium |

Total estimated financial exposure from potential data loss is **₹4.2 crore** (based on average IP valuation and breach cost models).

## 4. Recommendations  

1. **Automate stale‑account remediation** – Implement a Lambda function to disable IAM users inactive >60 days and notify owners.  
2. **Mandate hardware‑based MFA** for all production access (YubiKey or RSA token) by **31 Oct 2026** (coinciding with Diwali downtime).  
3. **Re‑scope service‑account permissions** – Apply least‑privilege principle; use IAM policy simulator for validation.  
4. **Correct CloudTrail retention** – Set S3 lifecycle to retain logs for 365 days; back‑fill missing logs from backup snapshots.  
5. **Encrypt all backup media** – Deploy LUKS encryption on NAS volumes; verify with quarterly compliance checks.  

Estimated remediation cost: **₹1.8 crore** (including tooling, licensing, and staff hours).

## 5. Action Plan & Timeline  

| Milestone | Owner | Target Date | Status |
|-----------|-------|-------------|--------|
| Deploy automated stale‑account script | Rohit Mehta | 15 Sep 2026 | In‑progress |
| Procure & distribute hardware MFA tokens | Ananya Rao | 30 Sep 2026 | Planned |
| Review & adjust service‑account policies | IAM Team | 10 Oct 2026 | Not started |
| Update CloudTrail lifecycle & back‑fill logs | Cloud Ops | 20 Oct 2026 | Not started |
| Encrypt on‑prem backups | Infra Team | 05 Nov 2026 | Not started |

All milestones will be tracked in the internal ticketing system (PKC‑SEC‑2026‑001). Weekly status meetings will be held every **Monday** at **10:00 IST** (via Teams). For any escalations, contact Ananya Rao at **+91‑80‑1234 5678**.

## 6. Appendices  

- **Appendix A** – Detailed IAM permission matrix (Excel attachment).  
- **Appendix B** – Log‑retention policy amendment draft.  
- **Appendix C** – Cost‑benefit analysis of MFA hardware vs. software tokens.  

*Prepared by the Security Assurance Team, PKC Technologies – Engineering Division.*