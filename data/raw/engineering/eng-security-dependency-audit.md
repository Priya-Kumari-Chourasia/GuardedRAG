---
doc_id: eng-security-dependency-audit
doc_class: security_review
department: engineering
title: "Security Review — Dependency Vulnerability Audit"
contains_pii: false
special_case: null
---

# Security Review — Dependency Vulnerability Audit

## Overview  
The Dependency Vulnerability Audit was conducted from **12 Mar 2026** to **28 Mar 2026** by the Engineering Security Team (EST) to assess the risk exposure of third‑party libraries used across PKC Technologies’ product stack. The audit covered all services deployed in the Bengaluru data centre and the Austin satellite office, focusing on the **Node.js**, **Python**, and **Java** ecosystems.  

## Scope & Methodology  
- **Assets Reviewed:** 112 micro‑services (Bengaluru: 84, Austin: 28)  
- **Libraries Scanned:** 3,487 distinct packages (npm: 1,842, PyPI: 1,021, Maven: 624)  
- **Tools Used:** OWASP Dependency‑Check v7.4, Snyk Enterprise, GitHub Dependabot alerts, internal SBOM generator.  
- **Risk Rating:** CVSS v3.1 base scores mapped to PKC’s internal risk matrix (Critical ≥ 9.0, High 7.0‑8.9, Medium 4.0‑6.9, Low < 4.0).  

## Findings Summary  

| Severity | # of Vulnerabilities | Affected Services | Estimated Remediation Cost |
|----------|---------------------|-------------------|-----------------------------|
| Critical | 7 | 5 (payment‑gateway, auth‑service, analytics‑engine, AI‑model‑trainer, CI pipeline) | ₹2.3 crore |
| High     | 24 | 18 | ₹1.1 crore |
| Medium   | 58 | 42 | ₹48 L |
| Low      | 112 | 67 | ₹12 L |

- **Critical Issues:**  
  1. **CVE‑2025‑12345** (log4j‑core 2.17.0) – Remote code execution, CVSS 9.8, present in the **analytics‑engine** (Bengaluru).  
  2. **CVE‑2025‑67890** (express‑4.18.2) – Prototype pollution, CVSS 9.3, affecting **payment‑gateway** API.  
  3. **CVE‑2025‑54321** (tensorflow‑2.12.0) – Arbitrary file read, CVSS 9.0, in **AI‑model‑trainer** (Austin).  

- **High Issues:** Predominantly outdated **lodash**, **urllib3**, and **spring‑boot** versions with known denial‑of‑service vectors.  

## Financial Impact  
- **Total projected remediation spend:** **₹4.0 crore** (including third‑party support contracts, additional QA cycles, and overtime).  
- **Potential loss avoidance:** Based on the 2025 breach cost benchmark for Indian SaaS firms (≈ ₹12 crore per incident), the audit is projected to mitigate an estimated **₹84 crore** in exposure.  

## Action Plan  

| Timeline | Milestone | Owner | Contact |
|----------|-----------|-------|---------|
| **31 Mar 2026** | Patch critical CVEs in production | Lead Engineer – Ananya Rao | +91‑80‑2345‑6789 |
| **15 Apr 2026** | Complete high‑severity updates & regression testing | DevOps Manager – Rohan Mehta | +91‑80‑3456‑7890 |
| **30 Apr 2026** | Publish updated SBOMs to internal registry | Security Analyst – Priya Singh | +91‑80‑4567‑8901 |
| **15 May 2026** | Conduct post‑remediation verification audit | EST Lead – Vikram Patel | +91‑80‑5678‑9012 |
| **31 May 2026** | Review and update dependency policy (aligned with PKC’s “Secure Code” guidelines) | Head of Engineering – Suman Gupta | +91‑80‑6789‑0123 |

All remediation work will observe **Republic Day** (26 Jan 2026) and **Mahashivratri** (17 Feb 2026) holidays; no production deployments are scheduled on these dates.  

## Recommendations  

1. **Automate Dependency Updates:** Enable Dependabot across all repositories with a mandatory PR review window of 48 hours.  
2. **Introduce a Quarterly SBOM Review:** Allocate ₹6 L per quarter for tooling licences and analyst time.  
3. **Establish a Vendor‑Managed Patch Window:** Negotiate SLA clauses with key third‑party vendors for critical patches within 72 hours of disclosure.  

The EST will circulate the detailed vulnerability report and remediation tickets by **02 Apr 2026**. Continuous monitoring will be enforced via Snyk alerts integrated with Slack (PKC‑Sec channel).  

---  
*Prepared by:*  
Vikram Patel, Lead – Security Review, Engineering  
PKC Technologies, Bengaluru – +91‑80‑5678‑9012  
---  