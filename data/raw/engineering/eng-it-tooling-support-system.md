---
doc_id: eng-it-tooling-support-system
doc_class: architecture_doc
department: engineering
title: "IT Support Ticketing System — Internal Tooling"
contains_pii: false
special_case: null
---

# IT Support Ticketing System — Internal Tooling

## 1. Overview  
The **IT Support Ticketing System (ITSTS)** is an internal, web‑based tool that consolidates all employee‑raised IT incidents, service requests, and asset tracking for PKC Technologies. It replaces the legacy email‑based workflow used since 2018 and aligns with the company’s 2025 Digital‑First Initiative. The system is hosted on PKC’s private Kubernetes cluster in the Bengaluru data centre and is replicated to the Austin satellite office for DR and latency optimisation.

## 2. Scope  
- **User Types** – Employees, IT Support Engineers, Service Managers, and Auditors.  
- **Supported Channels** – Web portal, mobile app (iOS/Android), and email gateway (support@pkc.in).  
- **Integration Points** – LDAP (for SSO), Slack (notification bot), Jira (escalation), and ServiceNow (CMDB sync).  
- **Compliance** – ISO 27001, GDPR (for US staff), and Indian IT Act 2000.

## 3. Architecture Overview  
| Layer | Technology | Rationale |
|-------|------------|-----------|
| Front‑end | React 18 + Material‑UI | Fast SPA, reusable components, mobile‑responsive. |
| API Gateway | Kong (v2.8) | Centralised routing, rate‑limiting, JWT validation. |
| Business Logic | Spring Boot 3 (Java 21) | Mature ecosystem, easy integration with existing PKC services. |
| Data Store | PostgreSQL 15 (primary) + TimescaleDB for metrics | ACID compliance, time‑series analytics for SLA reporting. |
| Search | Elasticsearch 8 | Full‑text ticket search, auto‑suggest. |
| Messaging | Apache Kafka 3.3 (topic: `itsts-events`) | Event‑driven updates to Slack and Jira. |
| Containerisation | Docker 24 + Helm charts | Consistent deployments across Bengaluru & Austin clusters. |
| Monitoring | Prometheus + Grafana | Real‑time dashboards, alerting on latency > 2 s. |
| CI/CD | GitHub Actions + ArgoCD | Automated testing, blue‑green deployments. |

## 4. Data Flow  
1. Employee logs in via SSO (LDAP) → JWT issued.  
2. Ticket creation POST `/api/v1/tickets` → validated by Kong, persisted in PostgreSQL.  
3. Event published to Kafka → Slack bot posts to `#it-support` channel, Jira ticket auto‑created.  
4. Service Engineer updates status → webhook triggers email to requester.  
5. Nightly ETL syncs asset data with ServiceNow CMDB.

## 5. Security & Compliance  
- **Encryption** – TLS 1.3 for all inbound/outbound traffic; data‑at‑rest encrypted with AWS KMS‑managed keys.  
- **Access Control** – Role‑Based Access Control (RBAC) enforced at API gateway.  
- **Audit Trail** – Immutable logs stored in S3‑compatible bucket for 12 months.  
- **Pen‑Test** – Quarterly external audit; last completed on 15‑02‑2025, no critical findings.

## 6. Deployment & SLA  
- **Production Roll‑out** – 01‑07‑2025 (Bengaluru) and 15‑07‑2025 (Austin).  
- **Uptime SLA** – 99.9 % monthly, with scheduled maintenance on the first Saturday of each month (excluding Republic Day 26‑01‑2025 and Diwali 15‑11‑2025).  
- **Incident Response** – Tier‑1 within 30 min, Tier‑2 within 2 h, Tier‑3 within 4 h.

## 7. Cost & Budget (FY 2025‑26)  
- **Initial CapEx** – ₹2.8 crore (hardware, licences, migration).  
- **Annual OpEx** – ₹1.15 crore (cloud hosting, support contracts).  
- **Projected Savings** – Reduction of manual ticket handling costs by ₹45 L per annum, ROI expected within 18 months.

## 8. Maintenance & Support  
- **Version Updates** – Quarterly minor releases; major releases aligned with PKC’s fiscal calendar (Q2).  
- **Support Contacts** –  
  - Primary: Ananya Rao, Lead Engineer – +91‑80‑1234 5678  
  - Backup: Michael Chen, DevOps Manager (Austin) – +1‑512‑555‑0199  

All queries should be logged via the internal portal or emailed to `it-support@pkc.in`.