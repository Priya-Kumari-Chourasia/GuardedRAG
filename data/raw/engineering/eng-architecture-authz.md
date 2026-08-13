---
doc_id: eng-architecture-authz
doc_class: architecture_doc
department: engineering
title: "Authentication and Authorization Design"
contains_pii: false
special_case: null
---

# Authentication and Authorization Design

## 1. Overview  

PKC Technologies (PKC) is building **SecureAuth**, a unified authentication‑authorization service for all internal SaaS products (PKC‑CRM, PKC‑Analytics, PKC‑Edge). The service will be deployed in the Bengaluru data centre (N‑Zone) and mirrored in the Austin satellite (US‑East) for latency‑critical workloads. The design complies with ISO 27001, GDPR (for EU customers) and the Indian Personal Data Protection Bill (PDPB).

*Document version:* v1.2 – 13 Aug 2026  
*Prepared by:* Ananya Rao, Lead Security Architect – +91‑80‑1234‑5678  

## 2. Threat Model  

| Threat | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| Credential stuffing (password spray) | Medium | High | Adaptive rate‑limiting, password‑less login (WebAuthn) |
| Insider privilege escalation | Low | Critical | Zero‑trust RBAC, Just‑In‑Time (JIT) access |
| Token replay (JWT) | Medium | Medium | Short‑lived access tokens (15 min), token binding |
| Supply‑chain compromise of third‑party libs | Low | High | SBOM verification, weekly SCA scans |

## 3. Design Overview  

- **Identity Provider (IdP):** OpenID Connect (OIDC) compliant, built on Keycloak 25.0.0, federated with Azure AD (for US staff) and LDAP (Bengaluru office).  
- **Authentication Methods:** Password + OTP, FIDO2/WebAuthn, and device‑based push (via PKC‑Auth app).  
- **Authorization Engine:** Policy‑Based Access Control (PBAC) using Open Policy Agent (OPA) with policies stored as Rego files in a GitOps repo.  
- **Token Format:** Signed JWT (RS256) with `kid` rotation every 30 days. Refresh tokens are opaque, stored in Redis‑Cluster (3‑node, 64 GB RAM).  

## 4. Authentication Flow  

1. **User initiates login** on PKC‑CRM → `/auth/login`.  
2. **PKC‑Auth Service** redirects to IdP OIDC `/authorize`.  
3. IdP validates credentials; if MFA required, triggers OTP via SMS (Twilio India) or push notification.  
4. Upon success, IdP issues **ID token** (valid 1 hour) and **access token** (15 min).  
5. Client stores tokens in HttpOnly secure cookies; subsequent API calls include `Authorization: Bearer <access‑token>`.  

*Key metrics:* Expected login latency ≤ 250 ms (Bengaluru) and ≤ 350 ms (Austin) under 10 k concurrent users.

## 5. Authorization Model  

- **Roles:** `admin`, `manager`, `analyst`, `viewer`.  
- **Permissions:** Defined per micro‑service (e.g., `crm:read`, `analytics:export`).  
- **Dynamic Scoping:** Contextual attributes (department, geo‑location) are evaluated at request time via OPA.  

## 6. Data Stores  

| Store | Purpose | Size (2026) | Cost |
|-------|---------|-------------|------|
| PostgreSQL‑13 (primary) | User profiles, MFA seeds | 2.4 TB | ₹8.5 L per month |
| Redis‑Cluster | Session & refresh tokens | 1.2 TB | ₹4.2 L per month |
| S3‑compatible (MinIO) | Audit logs (30 days) | 5 TB | ₹2.1 L per month |

## 7. Auditing & Logging  

- All auth events are streamed to **Kafka** topic `auth.audit` → **ElasticSearch** for SIEM.  
- Retention: 90 days (₹1.8 L annually).  
- Daily compliance report generated on **Republic Day** (26 Jan) and **Diwali** (Nov 12) for executive review.  

## 8. Compliance  

- **PDPB:** PII encrypted at rest (AES‑256) and in transit (TLS 1.3).  
- **GDPR:** Data‑subject access request (DSAR) workflow integrated with PKC‑Legal portal.  
- **ISO 27001:** Controls A.9 (Access Control) and A.12 (Cryptography) fully mapped.  

## 9. Deployment & Scaling  

- **Kubernetes (EKS‑Bengaluru, EKS‑Austin)** with auto‑scaling based on CPU > 70 % or request latency > 300 ms.  
- Blue‑Green deployments via ArgoCD; rollback window ≤ 5 min.  

## 10. Cost Estimates (Annual)  

- **Infrastructure:** ₹1.85 crore  
- **Third‑party services (SMS, S3, monitoring):** ₹42.7 L  
- **Staffing:** 4 engineers (₹18.4 L each) + 1 SRE (₹22.0 L) = ₹94.6 L  

**Total projected OPEX:** **₹3.12 crore**  

## 11. Risks & Mitigations  

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Token key compromise | Low | Dual‑key rotation, HSM‑backed signing |
| Vendor lock‑in (Keycloak) | Medium | Abstract IdP via OIDC façade, periodic migration drills |
| Regulatory change (PDPB) | Medium | Quarterly legal audit, policy versioning in GitOps |

## 12. References  

- PKC‑Sec‑Policy v4.3 (internal) – https://intranet.pkctechnologies.com/sec-policy  
- NIST SP 800‑63B – Digital Identity Guidelines  
- OIDC Core 1.0 – https://openid.net/specs/openid-connect-core-1_0.html  