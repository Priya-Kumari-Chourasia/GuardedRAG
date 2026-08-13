---
doc_id: eng-architecture-data-pipeline
doc_class: architecture_doc
department: engineering
title: "Data Pipeline and Storage Architecture"
contains_pii: false
special_case: null
---

# Data Pipeline and Storage Architecture

## 1. Overview  

PKC Technologies operates a hybrid‑cloud data platform that supports AI model training, real‑time analytics for our SaaS products, and compliance reporting for government contracts. The architecture is built around three logical layers – **Ingestion**, **Processing & Enrichment**, and **Storage & Retrieval** – and is hosted across our Bengaluru data centre (primary) and the Austin satellite office (disaster‑recovery). The design targets a sustained ingest rate of **5 TB/day**, a peak query concurrency of 1,200 QPS, and a 99.9 % SLA for all critical pipelines.

## 2. Ingestion Layer  

| Component | Vendor / Tech | Capacity | Monthly Op‑Ex |
|-----------|---------------|----------|---------------|
| Kafka Cluster (3‑zone) | Confluent Enterprise | 10 TB/day (burst 15 TB) | ₹1.2 crore |
| API Gateway (REST/GraphQL) | Kong + custom auth | 2 M req/day | ₹45 L |
| Edge Collectors (IoT) | Python‑based agents | 500 GB/day | ₹12 L |

All inbound traffic is TLS‑encrypted (TLS 1.3) and logged to **AWS CloudTrail** (replicated to Azure Monitor for cross‑cloud visibility). The ingestion team (8 engineers, avg. salary ₹22 L) works in two shifts to cover the Indian holidays calendar (e.g., Republic Day 26 Jan, Diwali 15 Nov) and US holidays (e.g., Independence Day 4 Jul) without service interruption.

## 3. Processing & Enrichment  

- **Stream Processing:** Apache Flink on Kubernetes (EKS) with autoscaling pods (min 30, max 120). Average CPU utilisation 68 %, costing ₹2.8 crore per annum.  
- **Batch Jobs:** Spark on EMR for nightly model‑training datasets (≈ 30 TB). Scheduled via Airflow (v2.5) with DAG SLA of 2 h.  
- **Data Quality:** Great Expectations integrated with Delta Lake; alerts routed to PagerDuty (₹6 L yearly).  

The processing team (12 members, avg. salary ₹25 L) collaborates with the Data Science unit to embed feature engineering logic directly into the pipeline, reducing model‑retraining latency from 48 h to 12 h.

## 4. Storage & Retrieval  

| Storage Tier | Tech | Size (as of 30 Jun 2026) | Annual Cost |
|--------------|------|--------------------------|-------------|
| Hot (real‑time) | Delta Lake on S3 (multi‑region) | 180 TB | ₹1.5 crore |
| Warm (analytics) | Azure Synapse Dedicated SQL Pool | 350 TB | ₹2.1 crore |
| Cold (archival) | Google Cloud Archive | 1.2 PB | ₹0.9 crore |

Data is partitioned by **event_date** and **region_id** to enable predicate push‑down. Access control is enforced via IAM roles mapped to PKC’s LDAP groups; all queries are audited and stored for 180 days to satisfy ISO 27001 and Indian IT Act 2000 requirements.

## 5. Security & Governance  

- **Encryption at rest:** AES‑256 managed keys (AWS KMS, Azure Key Vault).  
- **Network security:** VPC‑peered with private link to Austin DR site; traffic filtered through Palo Alto firewalls (₹3 L CAPEX).  
- **Compliance:** Quarterly reviews aligned with the Indian Financial Year (April – March) and the US fiscal calendar for the Austin office.  

## 6. Cost Summary (FY 2026‑27)  

- **Infrastructure (cloud + on‑prem):** ₹5.5 crore  
- **Staffing (engineering & ops):** ₹3.2 crore  
- **Licensing & SaaS:** ₹1.1 crore  
- **Total OPEX:** **₹9.8 crore**  

Projected ROI is 18 % over the next three years, driven by reduced model‑training cycles and a new analytics‑as‑a‑service offering slated for launch on **15 Oct 2026** (coinciding with the post‑Diwali rollout window).

## 7. Contact & Escalation  

- **Architecture Lead:** Ananya Rao – +91‑98765 43210 – ananya.rao@pkc.tech  
- **Operations Manager (Bengaluru):** Raghav Menon – +91‑99887 65432 – raghav.m@pkc.tech  
- **DR Coordinator (Austin):** Mike Chen – +1‑512‑555‑0198 – mike.chen@pkc.tech  

All critical incidents must be logged in ServiceNow within **30 minutes** of detection; SLA breach notifications are escalated to the CTO on the next working day (excluding Indian public holidays).