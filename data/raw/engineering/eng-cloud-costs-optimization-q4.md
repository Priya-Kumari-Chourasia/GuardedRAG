---
doc_id: eng-cloud-costs-optimization-q4
doc_class: cloud_costs
department: engineering
title: "Cloud Cost Optimization Recommendations — Q4 2025"
contains_pii: false
special_case: null
---

# Cloud Cost Optimization Recommendations — Q4 2025

## Executive Summary  

PKC Technologies’ cloud spend for Q4 2025 (1 Oct 2025 – 31 Dec 2025) is projected at **₹3.78 crore** across AWS, Azure, and GCP. Historical analysis (FY 2024‑25) shows a YoY increase of **28 %**, driven primarily by under‑utilised compute instances and redundant storage. By implementing the recommendations below, we anticipate a **22 % reduction** (≈ ₹83 L) without impacting SLA commitments for our flagship products – PKC‑Analytics, PKC‑ChatBot, and the internal CI/CD pipeline.

## Current Cost Breakdown  

| Service | Monthly Spend (₹) | Q4 2025 Total (₹) | Utilisation % |
|---------|-------------------|------------------|---------------|
| Compute (EC2, VM, GKE) | ₹1.12 crore | ₹3.36 crore | 38 % |
| Storage (S3, Blob, CloudSQL) | ₹45.6 L | ₹1.37 crore | 62 % |
| Data Transfer & CDN | ₹12.4 L | ₹37.2 L | 71 % |
| Managed Services (RDS, Azure Functions) | ₹9.8 L | ₹29.4 L | 55 % |
| Misc (Licensing, Support) | ₹5.2 L | ₹15.6 L | N/A |

## Key Recommendations  

### 1. Rightsize Compute Instances  
- **Action:** Deploy AWS Compute Optimizer and Azure Advisor to identify over‑provisioned VMs.  
- **Target:** Downsize 27 % of `t3.large` and `Standard_D4s_v3` instances to `t3.medium` / `Standard_D2s_v3`.  
- **Savings:** **₹12.5 L** per quarter.  

### 2. Implement Auto‑Scaling & Spot Instances  
- **Action:** Enable auto‑scaling groups for PKC‑Analytics batch jobs and migrate 15 % of non‑critical workloads to Spot/Preemptible VMs.  
- **Target:** Reduce on‑demand compute cost by **₹8.3 L**.  

### 3. Consolidate Storage & Enforce Lifecycle Policies  
- **Action:** Move cold data older than 180 days from S3 Standard to S3 Glacier Deep Archive; apply Azure Blob tiering for logs > 90 days.  
- **Target:** Delete orphaned snapshots (≈ 4.2 TB).  
- **Savings:** **₹6.7 L** per quarter.  

### 4. Optimize Data Transfer & CDN Usage  
- **Action:** Enable HTTP/2 and Brotli compression on edge nodes; route internal traffic via VPC peering instead of public internet.  
- **Target:** Cut outbound data transfer by 18 %.  
- **Savings:** **₹3.1 L**.  

### 5. Review Managed Service Licenses  
- **Action:** Conduct a quarterly audit of RDS instances and Azure Functions plans; downgrade 2 RDS instances from `db.m5.large` to `db.t3.medium`.  
- **Savings:** **₹2.4 L**.  

### 6. Governance & Monitoring Enhancements  
- **Action:** Deploy CloudHealth dashboard with cost alerts set to **₹5 L** threshold; schedule monthly review meetings on the first Thursday after Diwali (i.e., 13 Nov 2025).  
- **Benefit:** Early detection of cost anomalies, preventing overruns.  

## Implementation Timeline  

| Week | Milestone | Owner |
|------|-----------|-------|
| 1‑2 (1‑14 Oct) | Baseline audit & rightsizing scripts | Rajesh Kumar (Cloud Ops Lead) |
| 3‑4 (15‑31 Oct) | Spot instance pilot for PKC‑ChatBot | Priya Nair (DevOps Engineer) |
| 5‑6 (1‑15 Nov) | Storage lifecycle policy rollout | Anil Mehta (Data Platform) |
| 7‑8 (16‑30 Nov) | CDN compression & VPC peering | Suman Rao (Network Architect) |
| 9‑10 (1‑15 Dec) | License audit & downgrade | Kavita Sharma (DB Admin) |
| 11‑12 (16‑31 Dec) | Dashboard go‑live & final reporting | Rohan Patel (Finance – Cloud Cost) |

## Contact & Escalation  

- **Primary Owner:** Rajesh Kumar – Cloud Operations, +91‑80‑2345 6789, rajesh.kumar@pkc.tech  
- **Backup Owner:** Priya Nair – DevOps, +91‑80‑9876 5432, priya.nair@pkc.tech  
- **Finance Liaison:** Rohan Patel – +91‑80‑1122 3344, rohan.patel@pkc.tech  

All teams are requested to align their sprint deliverables with the above timeline and report any blockers by **5 Nov 2025** (post‑Diwali). Successful execution will position PKC Technologies to reinvest **₹83 L** into R&D for FY 2026‑27, reinforcing our competitive edge in AI‑driven solutions.