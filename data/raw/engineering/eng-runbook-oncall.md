---
doc_id: eng-runbook-oncall
doc_class: runbook
department: engineering
title: "Runbook — On-Call Escalation Process"
contains_pii: false
special_case: null
---

# Runbook — On-Call Escalation Process

## 1. Purpose & Scope  
This runbook defines the **On‑Call Escalation Process** for the Engineering department of PKC Technologies (PKC). It applies to all production services hosted in Bengaluru (primary data‑center) and the satellite office in Austin, USA. The process covers incident detection, initial response, escalation through three levels, and post‑mortem hand‑over.

---

## 2. On‑Call Rotation & Compensation  
| Rotation | Duration | Daily Shift | On‑Call Allowance | Overtime Rate |
|----------|----------|-------------|-------------------|---------------|
| Bengaluru | 2 weeks on / 2 weeks off | 08:00‑20:00 (Day) / 20:00‑08:00 (Night) | ₹12 L per annum (≈ ₹1 L per month) | ₹2.5 k per incident (beyond SLA) |
| Austin | 2 weeks on / 2 weeks off | 08:00‑20:00 CST / 20:00‑08:00 CST | ₹8 L per annum (≈ ₹66 k per month) | ₹2.5 k per incident |

**Holiday Adjustments** – On Indian public holidays (e.g., **26 Jan – Republic Day**, **15 Aug – Independence Day**, **Diwali – 1 Nov 2026**) the Bengaluru on‑call roster is extended by one day; the Austin team provides backup coverage.

---

## 3. Roles & Responsibilities  

| Role | Primary Owner | Contact (Phone) | Email |
|------|---------------|-----------------|-------|
| **Primary On‑Call Engineer (L1)** | Assigned Engineer | +91‑80‑1234 5678 (Bengaluru) / +1‑512‑555‑0199 (Austin) | l1‑oncall@pkc.tech |
| **Secondary Engineer (L2)** | Senior Engineer | +91‑80‑8765 4321 | l2‑oncall@pkc.tech |
| **Engineering Manager (L3)** | Sr. Manager – Platform | +91‑80‑1122 3344 | eng‑mgr@pkc.tech |
| **Incident Commander (IC)** | Rotating Lead (PM) | +91‑80‑9988 7766 | ic‑lead@pkc.tech |

---

## 4. Escalation Timeline  

| Time Since Alert | Action | Owner |
|------------------|--------|-------|
| **0‑15 min** | Acknowledge alert in PagerDuty, perform basic triage, attempt self‑remediation. | L1 |
| **15‑30 min** | If unresolved, notify L2 via Slack **#oncall‑escalation** and phone. | L1 |
| **30‑60 min** | L2 takes ownership, escalates to L3 if root cause > 30 min or impact > ₹5 L revenue loss. | L2 |
| **> 60 min** | L3 convenes Incident Commander, initiates war‑room (Zoom link: `https://zoom.pkctechnologies.com/IC`). | L3 |

All escalations must be logged in the **PKC Incident Tracker (Jira Project PKC‑INC)** with timestamps.

---

## 5. Communication Channels  

* **PagerDuty** – primary alerting system.  
* **Slack** – `#oncall‑bengaluru`, `#oncall‑austin`, and `#incident‑warroom`.  
* **Phone** – use the numbers in the role matrix; for urgent escalation, send an SMS with “ESCALATE” keyword.  
* **Email** – summary to `ops‑review@pkc.tech` within 2 hours of resolution.

---

## 6. Service Level Objectives (SLO)  

* **Mean Time to Acknowledge (MTTA)** ≤ 5 min.  
* **Mean Time to Resolve (MTTR)** ≤ 2 hrs for P1 incidents (impact > ₹10 L).  
* **Resolution SLA** – 4 hrs for P2, 8 hrs for P3.  

Failure to meet SLO triggers a **₹2 L** penalty to the responsible engineering pod (charged to the pod’s budget).

---

## 7. Post‑Incident Review  

1. **Incident Report** – completed within 24 hrs, stored in Confluence under *PKC/Incidents/2026*.  
2. **Root‑Cause Analysis (RCA)** – 48‑hour deadline; includes cost impact (e.g., “Revenue loss: ₹18.4 L”).  
3. **Action Items** – assigned to owners with due dates; tracked in Jira.  
4. **Monthly Review** – first Monday of each month (e.g., **5 Feb 2026**) at 10:00 IST, chaired by the Engineering Manager.  

---

## 8. Exceptions & Special Cases  

* **Planned Maintenance** – alerts suppressed via maintenance windows; on‑call engineers receive a **₹1 L** bonus for each successful blackout.  
* **Major Outage (> ₹50 L impact)** – immediate activation of the **PKC Business Continuity Team** (phone: +91‑80‑5555 1212).  

---

## 9. Document Control  

* **Version**: 1.3  
* **Effective Date**: 01 Jan 2026  
* **Owner**: Engineering Operations, PKC Technologies  
* **Review Cycle**: Quarterly (next review: 01 Apr 2026)  

---