---
doc_id: eng-cloud-costs-q3-2025
doc_class: cloud_costs
department: engineering
title: "Cloud Cost Report — Q3 2025"
contains_pii: false
special_case: cross_ref
---

# Cloud Cost Report — Q3 2025

## Executive Summary  
The Q3 2025 cloud cost report for PKC Technologies (Engineering) shows an AWS spend of **₹18.4 L**, representing a **12 % increase** over Q2 2025’s **₹16.4 L**. The uptick is primarily attributable to the rollout of the **PKC‑Recommend** service, which drove a 28 % rise in EC2 compute hours across our Bengaluru data centre region (ap‑south‑1). Despite the increase, the cost‑per‑transaction metric improved from ₹0.42 to ₹0.38, reflecting higher utilisation efficiency.

## Cloud Spend Overview  

| Category | Q3 2025 Spend | Q2 2025 Spend | Δ YoY | % of Total |
|----------|--------------|--------------|------|------------|
| Compute (EC2, Fargate) | ₹9.2 L | ₹7.1 L | +₹2.1 L | 50 % |
| Storage (S3, EBS) | ₹3.6 L | ₹3.4 L | +₹0.2 L | 20 % |
| Database (RDS, DynamoDB) | ₹2.8 L | ₹2.5 L | +₹0.3 L | 15 % |
| Networking & CDN (CloudFront, Data Transfer) | ₹1.5 L | ₹1.3 L | +₹0.2 L | 8 % |
| Miscellaneous (Lambda, Monitoring, Support) | ₹1.3 L | ₹1.1 L | +₹0.2 L | 7 % |
| **Total AWS Spend** | **₹18.4 L** | **₹16.4 L** | **+₹2.0 L** | **100 %** |

*All figures are in Indian Rupees (₹) and rounded to the nearest lakh.*

## Key Cost Drivers  

1. **PKC‑Recommend Service Launch (15 Aug 2025 – Independence Day)**  
   - Deployed on 12 new EC2 m5.4xlarge instances for real‑time inference.  
   - Compute usage rose from 12,400 instance‑hours (Q2) to 15,900 instance‑hours (Q3).  

2. **Data Lake Expansion**  
   - Added 3 PB of raw click‑stream data to S3, increasing storage cost by ₹0.2 L.  

3. **Regional Traffic Spike**  
   - Post‑Gandhi Jayanti (2 Oct 2025) marketing campaign generated a 15 % surge in CDN traffic, adding ₹0.15 L to CloudFront charges.  

## Optimization Initiatives  

| Initiative | Owner | Timeline | Expected Savings |
|------------|-------|----------|------------------|
| Right‑size EC2 instances (use of Spot & Savings Plans) | Arjun Mehta, Cloud Ops Lead | Sep 2025 – Dec 2025 | ₹1.2 L / yr |
| Enable S3 Intelligent‑Tiering for infrequently accessed logs | Priya Nair, Data Engineering | Oct 2025 | ₹0.4 L / yr |
| Adopt Aurora Serverless for low‑traffic micro‑services | Karan Singh, DB Admin | Nov 2025 | ₹0.3 L / yr |
| Consolidate CloudWatch metrics into unified dashboards | Ritu Sharma, DevOps | Dec 2025 | ₹0.1 L / yr |

Progress to date: Spot instance adoption has already reduced compute spend by **₹0.35 L** (≈3.8 % of Q3 total).

## Forecast & Recommendations  

- **Q4 2025 Projection:** Assuming a modest 5 % growth in traffic and full implementation of the above initiatives, projected AWS spend is **₹19.0 L**.  
- **Recommendation:** Prioritise Spot‑instance migration for batch jobs and enforce lifecycle policies on S3 objects older than 90 days.  
- **Risk Mitigation:** Maintain a buffer of **₹0.5 L** for unexpected spikes (e.g., festive season traffic) and review Reserved Instance commitments quarterly.

## Contacts  

- **Cloud Cost Owner:** Arjun Mehta – +91‑80‑1234 5678  
- **Finance Liaison:** Meera Patel – +91‑80‑8765 4321  
- **Engineering Lead (PKC‑Recommend):** Sandeep Rao – +91‑80‑1122 3344  

For detailed line‑item breakdowns, refer to the attached **AWS Cost Explorer** CSV (Q3 2025) in the internal repository.