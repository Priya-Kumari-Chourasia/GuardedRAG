---
doc_id: eng-postmortem-api-outage-sep
doc_class: postmortem
department: engineering
title: "Postmortem — September 2025 API Outage"
contains_pii: false
special_case: null
---

# Postmortem — September 2025 API Outage

## Summary  
On **12 September 2025 (Saturday)**, PKC Technologies experienced a critical outage of its public **v1.3 API** used by over 1,200 B2B clients. The service was unavailable for **7 hours 45 minutes**, causing an estimated **₹3.2 crore** loss in billable usage and triggering SLA breach penalties of **₹45 L**. The incident was fully resolved by **20:15 IST** on the same day.

## Timeline  

| Time (IST) | Event |
|------------|-------|
| 02:30 – 02:45 | Automated monitoring alerts (Datadog) indicate 504 errors from API gateway. |
| 02:46 – 03:00 | On‑call engineer **Ananya Rao** (L2) acknowledges alerts, escalates to **Sanjay Mehta** (L3). |
| 03:01 – 03:20 | Investigation reveals a sudden spike in Redis cache eviction rates. |
| 03:21 – 04:00 | Attempted cache warm‑up fails; team initiates a full service restart. |
| 04:01 – 04:45 | Restart triggers a cascading failure in the **Kubernetes** node pool due to a mis‑configured **PodDisruptionBudget**. |
| 04:46 – 06:30 | Engineers manually scale the node pool (add 4 nodes) and apply a hot‑fix to the PDB. |
| 06:31 – 07:15 | API returns 200 responses for internal health checks; external traffic still blocked by **NGINX** rate‑limit rules. |
| 07:16 – 08:45 | Rate‑limit thresholds adjusted; traffic gradually restored. |
| 08:46 – 09:30 | Full functional verification completed; monitoring shows normal latency (< 120 ms). |
| 09:31 – 20:15 | Post‑mortem data collection, stakeholder communication, and incident report drafting. |
| 20:20 – 20:30 | Incident closure meeting; action items assigned. |

## Impact  

- **Clients affected:** 1,237 (including major partners **FinEdge**, **HealthSync**, **EduBridge**).  
- **Revenue impact:** Approx. **₹3.2 crore** (lost API call revenue).  
- **SLA penalties:** **₹45 L** (per contract terms).  
- **Support tickets:** 184 tickets opened; average resolution time 3 hours.  
- **Customer sentiment:** NPS dropped from **+42** to **+28** for the week.  

## Root Cause  

1. **Cache Saturation:** A newly released feature (bulk‑data export) generated a **3.8×** increase in Redis key count, exceeding the allocated **8 GB** memory.  
2. **Mis‑configured PodDisruptionBudget:** The PDB allowed only 1 pod disruption, but the restart required 2 simultaneous pod terminations, causing the node pool to become unresponsive.  
3. **Insufficient Rate‑Limit Guardrails:** NGINX limits were set to **500 rps** per IP; the sudden traffic surge after cache warm‑up breached this, blocking legitimate client requests.  

## Mitigation Steps (During Incident)  

- Added **4** additional nodes to the Kubernetes cluster (cost **₹2.5 L**).  
- Applied a temporary **Redis eviction policy** change to **volatile‑ttl**.  
- Updated NGINX rate‑limit to **1,200 rps** per IP.  

## Action Items  

| Owner | Action | Due Date |
|-------|--------|----------|
| **Ananya Rao** (SRE Lead) | Increase Redis memory to **12 GB** and enable **active‑defragmentation**. | 30 Sept 2025 |
| **Sanjay Mehta** (Platform Engineer) | Redesign PodDisruptionBudget to allow **2** concurrent disruptions and add automated PDB validation CI test. | 15 Oct 2025 |
| **Rohit Patel** (API Product) | Implement adaptive rate‑limit thresholds based on real‑time traffic patterns. | 05 Nov 2025 |
| **Priya Nair** (Customer Success) | Draft client communication template and schedule follow‑up calls with top‑10 impacted accounts. | 20 Sept 2025 |
| **Finance Team** | Reconcile SLA penalty payout and adjust quarterly forecast (reduce projected revenue by **₹45 L**). | 25 Sept 2025 |

## Follow‑Up  

A post‑incident review meeting is scheduled for **22 September 2025** at **10:00 IST** (Zoom link: https://zoom.us/j/123456789). Minutes will be circulated to all stakeholders. For any urgent queries, contact the SRE on‑call at **+91‑80‑1234 5678** (ext 101).  

---  

*Prepared by the Engineering Post‑mortem Committee, PKC Technologies.*