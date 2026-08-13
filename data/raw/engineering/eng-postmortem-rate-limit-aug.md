---
doc_id: eng-postmortem-rate-limit-aug
doc_class: postmortem
department: engineering
title: "Postmortem — Rate Limit Incident, August 2025"
contains_pii: false
special_case: null
---

# Postmortem — Rate Limit Incident, August 2025

## Summary  
On **12 Aug 2025 (Thursday)**, PKC Technologies experienced a rate‑limit failure in the **AuthX** microservice that powers API authentication for all external partners. The issue persisted for **3 hours 45 minutes**, causing intermittent 429 responses for approximately **1.2 million** API calls. The incident was fully resolved by **16:30 IST** on the same day.  

## Timeline  

| Time (IST) | Event |
|------------|-------|
| 09:12 | Monitoring alert from Prometheus (authx_rate_limit_exceeded) triggered. |
| 09:15 | On‑call engineer **Rohit Mehta** (L2) acknowledged the alert. |
| 09:18 | Initial triage indicated a spike in request volume from the **PartnerConnect** integration. |
| 09:30 | Rate‑limit thresholds were manually increased from **500 rps** to **800 rps** to mitigate impact. |
| 10:05 | Spike persisted; logs showed a runaway loop in the **token‑refresh** endpoint. |
| 10:45 | Root cause identified: recent deployment (v2.4.1) introduced a missing cache‑invalidation flag. |
| 11:20 | Rollback of v2.4.1 initiated; deployment completed at 11:45. |
| 12:10 | Rate‑limit errors dropped below 1 % of traffic. |
| 12:30 | Full service health restored; monitoring returned to normal. |
| 16:30 | Post‑incident review call concluded; incident declared closed. |

## Impact  

* **External API consumers**: 1.2 M calls failed (≈ ₹9.6 L in SLA penalties).  
* **Revenue impact**: Estimated loss of **₹2.3 crore** due to delayed partner onboarding.  
* **Customer support tickets**: 842 tickets opened, average handling time 18 min.  
* **Internal productivity**: Engineering spent **≈ 120 person‑hours** on mitigation and rollback.  

## Root Cause  

The **v2.4.1** release (deployed on **10 Aug 2025**) added a new **token‑refresh** endpoint. A configuration flag (`CACHE_INVALIDATE_ON_REFRESH`) was mistakenly set to `false` in the production Helm chart, causing stale token entries to accumulate in Redis. This led to repeated authentication attempts and a cascade of rate‑limit breaches.  

## Mitigation & Recovery  

1. **Immediate**: Manual rate‑limit bump and temporary circuit‑breaker activation.  
2. **Rollback**: Reverted to **v2.4.0** (stable) and verified cache behavior.  
3. **Post‑mortem**: Added a health‑check for the flag in CI pipeline; introduced a canary rollout for future auth changes.  

## Action Items  

| Owner | Action | Due |
|-------|--------|-----|
| **Ananya Rao (SRE Lead)** | Implement automated validation of Helm flag values during deployment. | 30 Sep 2025 |
| **Karan Singh (Product Engineer)** | Add unit tests for cache‑invalidation logic in token‑refresh flow. | 15 Oct 2025 |
| **Priya Nair (QA Manager)** | Expand load‑testing suite to simulate 2× peak traffic for AuthX. | 05 Nov 2025 |
| **Finance Ops** | Process SLA penalty claim with partner **PartnerConnect** (₹9.6 L). | 20 Sep 2025 |
| **HR** | Conduct a brief “Incident Response Best Practices” refresher for on‑call engineers. | 01 Oct 2025 |

## Lessons Learned  

* **Configuration drift** can silently break critical paths; enforce strict config linting.  
* **Rate‑limit thresholds** should be dynamically adjustable based on real‑time traffic patterns.  
* A **post‑deployment health‑check** for key flags reduces manual verification overhead.  

For any follow‑up queries, contact the incident commander **Rohit Mehta** at **+91‑80‑12345678** or via Slack `@rohit.mehta`.  

---  

*Prepared by the Engineering Post‑mortem Team, PKC Technologies – Bengaluru*  