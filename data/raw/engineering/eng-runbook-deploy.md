---
doc_id: eng-runbook-deploy
doc_class: runbook
department: engineering
title: "Runbook — Production Deployment Procedure"
contains_pii: false
special_case: null
---

# Runbook — Production Deployment Procedure

## 1. Overview  
This runbook describes the end‑to‑end procedure for deploying a new release of the **PKC Core AI Platform** to the production environment (PKC‑PROD‑01). It is intended for the Engineering, DevOps, and QA teams and must be followed for every scheduled release to ensure consistency, compliance, and minimal downtime.

**Target release:** v3.7.2 (Feature set: Adaptive‑Learning Engine, Data‑Lake Optimiser)  
**Planned deployment window:** 02 Oct 2026 – 04 Oct 2026 (Mon‑Wed)  
**Maximum allowed outage:** 15 minutes per service tier  

## 2. Prerequisites  

| Item | Requirement | Owner |
|------|-------------|-------|
| Release package | Signed SHA‑256 checksum, stored in PKC‑ARTIFACTORY | Release Manager (Ananya Rao) |
| Infrastructure capacity | ≥ ₹2.5 crore of reserved compute (AWS + on‑prem) | Cloud Ops (Rohit Mehta) |
| Security audit | OWASP‑ZAP score ≥ 90 % | SecOps (Vikram Singh) |
| Change‑request approval | Approved in ServiceNow (CR‑2026‑1089) | Change Advisory Board (CAB) |
| Backup | Full DB snapshot (₹12.3 L) retained for 30 days | DBA Team (Leena Patel) |

All items must be verified **24 hours** before the deployment window.

## 3. Roles & Responsibilities  

| Role | Primary Contact | Phone |
|------|----------------|-------|
| Release Manager | Ananya Rao | +91‑80‑1234‑5678 |
| Lead DevOps Engineer | Rohit Mehta | +91‑80‑9876‑5432 |
| QA Lead | Priya Nair | +91‑80‑5555‑1122 |
| On‑call SRE | Karan Gupta | +91‑80‑7777‑3344 |
| Business Stakeholder | Sunil Deshmukh (Head of Product) | +91‑80‑6666‑7788 |

## 4. Deployment Steps  

1. **Pre‑deployment checklist (02 Oct 2026, 08:00 IST)**  
   - Verify backup integrity (checksum).  
   - Confirm no critical Indian holidays (e.g., **Gandhi Jayanti – 02 Oct**) clash with support staff availability.  

2. **Feature toggle freeze (08:30 IST)**  
   - Disable non‑essential toggles via PKC‑CONFIG‑SERVICE.  

3. **Blue‑Green switch (09:00 IST)**  
   - Spin up **PKC‑PROD‑BLUE** (₹1.8 crore) with new containers.  
   - Run health probes; ensure latency < 120 ms.  

4. **Database migration (09:45 IST)**  
   - Execute migration scripts (estimated runtime = 7 min).  
   - Monitor DB logs for errors; abort if > 2 failed rows.  

5. **Traffic shift (10:00 IST)**  
   - Gradually route 20 % traffic to blue environment using PKC‑INGRESS‑CTRL.  
   - Observe error rate; must stay < 0.2 %.  

6. **Full cut‑over (10:30 IST)**  
   - Switch 100 % traffic to blue; decommission green after 30 min grace period.  

7. **Post‑deployment smoke test (11:00 IST)**  
   - Run automated suite (≈ 150 tests).  
   - Validate key KPIs: API latency, model inference accuracy (≥ 98 %).  

## 5. Rollback Procedure  

If any KPI breaches thresholds:  

1. Trigger **Rollback Playbook v2.3** via ServiceNow (CR‑2026‑1091).  
2. Re‑attach traffic to **PKC‑PROD‑GREEN** within 5 minutes.  
3. Restore DB snapshot (₹12.3 L) and verify data integrity.  
4. Notify all stakeholders within 15 minutes of rollback initiation.  

## 6. Communication  

- **Pre‑release email** (24 h prior) to all engineering and product teams.  
- **Live status channel**: #pkc-prod-deploy on Slack (PKC‑Ops).  
- **Stakeholder briefing** (post‑deployment, 12:00 IST) via Zoom.  

## 7. Escalation Contacts  

| Level | Contact | Phone |
|-------|---------|-------|
| P1 – Critical outage | Karan Gupta (SRE Lead) | +91‑80‑7777‑3344 |
| P2 – Major degradation | Rohit Mehta (DevOps) | +91‑80‑9876‑5432 |
| P3 – Minor issue | Ananya Rao (Release Mgr) | +91‑80‑1234‑5678 |

Escalate to **PKC Incident Management** (on‑call rotation) if resolution exceeds 30 minutes.

## 8. Metrics & Reporting  

- **Deployment duration:** target ≤ 90 min.  
- **Mean Time to Recovery (MTTR):** ≤ 20 min (post‑rollback).  
- **Cost of deployment:** estimated ₹4.7 L (compute + licensing).  

All metrics are logged in **PKC‑METRICS‑DB** and a summary report is circulated to senior leadership by 18 Oct 2026.  

---  

*Prepared by the Engineering Runbook Team, PKC Technologies – Bengaluru (HQ) & Austin (Satellite).*