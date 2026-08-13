---
doc_id: eng-cloud-costs-aws-breakdown-sep
doc_class: cloud_costs
department: engineering
title: "AWS Cost Breakdown by Service — September 2025"
contains_pii: false
special_case: null
---

# AWS Cost Breakdown by Service — September 2025

## 1. Executive Summary  

For September 2025 the Engineering department incurred **₹2.84 crore** in AWS spend across all environments. Compared with August 2025 (₹2.61 crore) this represents a **+8.8 %** month‑on‑month increase, primarily driven by a post‑Ganesh Chaturthi data‑migration to the new **us‑west‑2** region and a temporary surge in EC2‑based model‑training workloads for the upcoming **PKC‑Vision** product launch.

---

## 2. Service‑wise Cost Breakdown  

| AWS Service | September 2025 Spend | % of Total | YoY Δ (Sep 2024) |
|-------------|---------------------|------------|-----------------|
| **EC2 (On‑Demand + Spot)** | ₹1.12 crore | 39.4 % | +12.5 % |
| **S3 (Standard + IA)** | ₹58.6 L | 20.6 % | +5.2 % |
| **RDS (Aurora MySQL)** | ₹42.3 L | 14.9 % | +3.1 % |
| **Lambda** | ₹21.4 L | 7.5 % | +2.8 % |
| **CloudFront** | ₹18.9 L | 6.6 % | +1.9 % |
| **EKS (Managed Nodes)** | ₹15.2 L | 5.3 % | +9.4 % |
| **Other (SNS, SQS, DynamoDB, etc.)** | ₹12.0 L | 4.2 % | +0.6 % |
| **Total** | **₹2.84 crore** | 100 % | +8.8 % |

*All figures are rounded to the nearest lakh.*

### 2.1 Project Allocation  

| Project | % of Total Spend | Cost (₹) |
|---------|------------------|----------|
| PKC‑Prod (Customer‑facing SaaS) | 55 % | ₹1.56 crore |
| PKC‑Dev (CI/CD & Test) | 28 % | ₹79.5 L |
| PKC‑Research (AI/ML experiments) | 17 % | ₹48.3 L |

---

## 3. Key Cost Drivers  

| Driver | Description | Impact |
|--------|-------------|--------|
| **Data Migration (Sep 2 – Sep 4)** | Transfer of 12 TB of training data to **us‑west‑2** after Ganesh Chaturthi holiday. Utilised **S3 Transfer Acceleration** and **EC2‑based copy scripts**. | +₹22 L (7.8 % of total) |
| **Model Training Spike** | Two new deep‑learning models (Vision‑V1, Vision‑V2) ran on **p3.2xlarge** Spot instances for 120 hrs each. | +₹31 L |
| **Reserved Instance (RI) Expiry** | 6 months of **m5.large** RIs expired on Sep 15, reverting to On‑Demand rates. | +₹9 L |
| **Increased CloudFront Traffic** | Post‑release of the **PKC‑Mobile** app (Sep 10) drove a 15 % rise in edge requests. | +₹4 L |

---

## 4. Recommendations  

1. **Accelerate RI Purchases** – Convert 75 % of the current On‑Demand EC2 usage (especially m5 & c5 families) to 1‑year RIs. Projected annual saving: **₹1.1 crore**.  
2. **Leverage Savings Plans for Lambda** – Adopt Compute Savings Plans covering the projected 2026 Lambda invocations. Estimated reduction: **₹2.5 L per month**.  
3. **Data Transfer Optimization** – Schedule large cross‑region transfers outside peak holiday windows and evaluate **AWS DataSync** for cost‑effective bulk moves.  
4. **Spot Fleet Governance** – Implement automated Spot‑Fleet termination policies to avoid overruns during price spikes; expected to curb EC2 overspend by **₹6 L** monthly.  

---

## 5. Action Items (Owner – Due Date)  

| Action | Owner | Due Date |
|--------|-------|----------|
| Submit RI purchase request for m5/c5 families (75 % coverage) | **Ananya Rao, Cloud Ops Lead** | 20‑Sep‑2025 |
| Configure Compute Savings Plan for Lambda (2025‑2026) | **Vikram Patel, DevOps Manager** | 25‑Sep‑2025 |
| Draft DataSync migration SOP for Q4 2025 | **Rohit Menon, Data Engineering** | 30‑Sep‑2025 |
| Update Spot‑Fleet policies in Terraform modules | **Sneha Iyer, Infrastructure Engineer** | 05‑Oct‑2025 |

---

## 6. Contact  

For any queries or deeper drill‑downs, please reach out to the Cloud Cost Governance team:  

- **Name:** Priya Nair  
- **Phone:** +91‑80‑1234‑5678  
- **Email:** priya.nair@pkctech.in  

*Prepared by the Engineering Cloud Cost Working Group on 12‑Sep‑2025.*