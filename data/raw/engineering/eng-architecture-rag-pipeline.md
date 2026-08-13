---
doc_id: eng-architecture-rag-pipeline
doc_class: architecture_doc
department: engineering
title: "RAG Pipeline Architecture Doc"
contains_pii: false
special_case: null
---

# RAG Pipeline Architecture Doc

## Overview
The Retrieval‑Augmented Generation (RAG) pipeline at **PKC Technologies** is designed to power our flagship products – **PKC‑Chat**, **InsightLens**, and the upcoming **CodeAssist**. The architecture combines a vector store, a large language model (LLM) hosted on our private GPU cluster, and a real‑time document ingestion service. The solution is fully compliant with Indian data‑privacy regulations (PDPA) and supports multi‑regional deployment for our Bengaluru headquarters and the Austin satellite office.

## Core Components

| Component | Description | Deployment | Monthly Cost (₹) |
|-----------|-------------|------------|------------------|
| Document Ingestion Service | Kafka‑based pipeline that normalises PDFs, DOCX, and code repos; extracts metadata and chunks (≈ 512‑token). | Bengaluru (primary) + Austin (fail‑over) | ₹12.5L |
| Vector Store (FAISS + Milvus) | Stores ~150M embeddings (≈ 2.4TB) with IVF‑PQ indexing for sub‑second similarity search. | 4x GPU‑enabled nodes (NVIDIA A100) | ₹9.8L |
| LLM Inference Engine | Fine‑tuned LLaMA‑2‑70B on our on‑prem cluster; supports LoRA adapters for domain‑specific prompts. | 6x GPU nodes (A100) + 2x CPU fallback | ₹22.3L |
| Orchestration (Kubernetes) | Helm‑managed charts with Istio service mesh; auto‑scales based on request latency SLA ≤ 300 ms. | Multi‑zone (Bengaluru‑1, Bengaluru‑2) | ₹5.6L |
| Monitoring & Logging | Prometheus + Grafana dashboards; Loki for log aggregation; alerts routed to Slack & PagerDuty. | Centralised (Bengaluru) | ₹2.1L |

**Total monthly OPEX:** **₹52.3L** (≈ ₹6.28 crore annually).

## Data Flow

1. **Ingestion** – New documents are pushed to the `pkc-docs` Kafka topic (retention 30 days). A Spark Structured Streaming job parses, cleans, and stores raw files in S3‑compatible storage (₹1.2L/month).  
2. **Chunking & Embedding** – Text is split using a sliding‑window algorithm; each chunk is embedded via the LLM’s encoder (≈ 0.45 ms per chunk).  
3. **Vector Indexing** – Embeddings are upserted into Milvus; nightly compaction reduces index size by 12 %.  
4. **Query Handling** – User query hits the API gateway (NGINX + JWT auth). The query is embedded, top‑k (k=5) nearest neighbours are retrieved, and the LLM generates a response conditioned on retrieved context.  
5. **Post‑Processing** – A rule‑based validator checks for PII leakage; flagged responses trigger a manual review workflow (via JIRA ticketing).  

## Security & Compliance

- **Data Residency:** All raw and processed data remain within Indian borders (Bengaluru data centre) except for anonymised logs sent to Austin for latency testing.  
- **Encryption:** TLS 1.3 for in‑flight traffic; AES‑256 at rest.  
- **Access Controls:** Role‑based access via Azure AD; privileged accounts require MFA and are reviewed quarterly (next review: **15 Oct 2026**, Republic Day holiday observed).  

## Team & Staffing

| Role | Name | Salary (₹) | Contact |
|------|------|------------|---------|
| Lead Architect | Ananya Rao | ₹32.5L | +91‑80‑12345678 |
| Senior ML Engineer | Karan Mehta | ₹28.0L | +91‑80‑23456789 |
| DevOps Engineer | Priya Singh | ₹22.5L | +91‑80‑34567890 |
| Data Engineer | Rohan Patel | ₹18.4L | +91‑80‑45678901 |
| QA Lead | Sunita Nair | ₹16.0L | +91‑80‑56789012 |

**Annual payroll:** **₹1.17 crore**.

## Roadmap (FY‑27)

- **Q1:** Deploy RAG‑v2 with hybrid retrieval (BM25 + vector) – target latency ≤ 250 ms.  
- **Q2:** Integrate multilingual embeddings (Hindi, Tamil, Bengali) – expected 15 % increase in token coverage.  
- **Q3:** Launch **CodeAssist** beta for internal developers – pilot with 120 users (incl. Austin team).  
- **Q4:** Achieve 99.9 % uptime SLA; conduct external audit ahead of Diwali (₹3.2L audit fee).  

## Contact & Support

For architecture queries, reach out to the engineering ops mailbox **eng-ops@pkc.tech** or call **+91‑80‑98765432** (Mon‑Fri, 09:00‑18:00 IST). Critical incidents are escalated via PagerDuty (on‑call rotation starts 01 Nov 2026).