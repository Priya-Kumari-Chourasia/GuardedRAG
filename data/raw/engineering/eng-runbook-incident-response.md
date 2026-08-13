---
doc_id: eng-runbook-incident-response
doc_class: runbook
department: engineering
title: "Runbook — Incident Response Checklist"
contains_pii: false
special_case: null
---

# Runbook — Incident Response Checklist

## 1. Purpose & Scope  
This runbook defines the step‑by‑step checklist for handling production incidents affecting PKC Technologies’ AI platforms (core inference service, data pipelines, and customer‑facing APIs). It applies to all services hosted in Bengaluru data‑centres and the AWS us‑east‑1 region used by the Austin satellite office.

## 2. Incident Detection  
| Trigger | Tool | Alert Channel | SLA |
|---------|------|---------------|-----|
| Service latency > 200 ms (5‑minute rolling avg) | New Relic | #eng‑alerts (Slack) | 15 min |
| Error‑rate > 5 % (HTTP 5xx) | Grafana Alertmanager | PagerDuty (on‑call) | 5 min |
| Data‑pipeline stall > 30 min | Airflow UI | Email to `data‑ops@pkc.in` | 10 min |

All alerts must be acknowledged within the SLA and a ticket created in JIRA (Project: **ENG‑INC**, Issue Type: Incident).

## 3. Roles & Responsibilities  
| Role | Primary Owner | Backup | Contact |
|------|----------------|--------|---------|
| Incident Commander (IC) | **Rohit Mehta** (SRE Lead) | **Ananya Rao** (Platform Engineer) | +91‑80‑1234‑5678 |
| Communications Lead | **Sneha Iyer** (Product Ops) | **Vikram Singh** (HR) | +91‑80‑8765‑4321 |
| Technical Lead – AI Services | **Karan Patel** (ML Engineer) | **Deepa Nair** (Data Engineer) | +91‑80‑1122‑3344 |
| On‑Call Engineer (Tier‑1) | Rotating roster – see **On‑Call Calendar** (₹12 L per annum stipend) | – | – |

## 4. Triage Checklist (within 30 min)  
1. Verify alert authenticity – check metric trends.  
2. Classify severity:  
   - **S1** – Full service outage (≥ 50 % user impact).  
   - **S2** – Degraded performance (≥ 20 % impact).  
   - **S3** – Minor issue (≤ 20 % impact).  
3. Update JIRA with severity, affected services, and initial ETA.  
4. Notify stakeholders via the **Incident Communication Channel** (Slack #inc‑comm).  

## 5. Containment Actions  
- **S1**: Trigger traffic‑shaping rule in Cloudflare (block offending IP range).  
- **S2**: Scale out affected pods (increase replica count by 2×).  
- **S3**: Apply hot‑fix patch from GitHub repo `pkc/ai‑service‑patches`.  

Document every command executed (e.g., `kubectl scale deployment inference‑svc --replicas=12`).

## 6. Eradication & Recovery  
1. Identify root cause (e.g., memory leak in `model‑loader` v2.3.1).  
2. Deploy rollback to previous stable version (v2.2.9).  
3. Run smoke tests (Postman collection `PKC‑API‑Smoke`).  
4. Gradually restore traffic (ramp‑up over 15 min).  

## 7. Post‑Incident Review (within 48 h)  
- Conduct **Post‑Mortem Meeting** (incl. SRE, Product, QA).  
- Complete **Post‑Mortem Report** (template stored in Confluence).  
- Record financial impact: e.g., downtime cost = **₹4.5 L** (based on SLA‑penalty of ₹1 crore per hour of outage).  
- Update runbook if gaps identified.  

## 8. Communication Protocol  
- **Internal**: Immediate updates on Slack; summary email to `engineering@pkc.in` after resolution.  
- **External**: If SLA breach occurs, notify customers via status page (status.pkc.in) and email template “PKC Service Incident – Update”.  
- **Regulatory**: For data‑loss incidents, report to the Data Protection Officer within 72 hours (per Indian IT Act).  

## 9. Escalation Matrix (Holiday Considerations)  
| Day | Escalation Path |
|-----|-----------------|
| Normal working day | IC → Communications Lead → VP Engineering (₹30 L annual salary) |
| Indian public holiday (e.g., **26 Jan – Republic Day**) | IC → On‑Call Engineer (next‑shift) → VP Engineering (via SMS) |
| Weekend (Sat‑Sun) | IC → On‑Call Engineer (first responder) → CTO (₹45 L annual salary) |

All escalations must be logged in JIRA with timestamps.

## 10. Tools & Access  
- **Monitoring**: New Relic, Grafana, Prometheus.  
- **Incident Management**: PagerDuty, JIRA, Confluence.  
- **Runbook Repository**: GitLab `pkc/runbooks` (protected branch `main`).  
- **Credentials**: Vault path `pkc/infra/production` (access granted via LDAP).  

---  

*Prepared by PKC Technologies – Engineering Ops (Version 1.3, effective 01 Oct 2024).*