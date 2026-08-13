---
doc_id: co-it-howto-password
doc_class: it_howto
department: company_wide
title: "IT How-To: Resetting Your Password"
contains_pii: false
special_case: null
---

# IT How-To: Resetting Your Password

## Purpose  
This guide outlines the standard procedure for resetting a corporate password for all PKC Technologies employees (Bengaluru HQ and Austin satellite). It ensures compliance with PKC’s security policy, minimizes downtime, and provides a clear escalation path.

## Scope  
Applicable to all staff, contractors, and interns who use PKC‑managed accounts (Active Directory, VPN, SaaS portals). The process is mandatory for password changes after 90 days, after a security incident, or when a user is locked out.

## Prerequisites  

| Requirement | Details |
|-------------|---------|
| Verified Identity | Government‑issued ID (Aadhaar/PAN) or employee badge number. |
| Approved Request | Must be logged in the IT Service Portal (ITSM) with a ticket number (e.g., PKC‑IT‑2024‑01873). |
| Device Access | User must have access to a PKC‑managed device or a registered mobile number (+91‑80‑1234‑5678). |

## Step‑by‑Step Reset Procedure  

1. **Open the IT Service Portal** – Navigate to `https://itsm.pkc.in` and log in with your current credentials.  
2. **Create a New Ticket** – Select *Password Reset* → *Self‑Service* → Fill in:  
   - Employee ID  
   - Registered mobile number  
   - Reason for reset (e.g., “Forgot password”, “Security policy expiry”).  
3. **OTP Verification** – An OTP will be sent to your registered mobile number. Enter the 6‑digit code within 5 minutes.  
4. **Temporary Password Generation** – The portal will display a temporary password (valid for 30 minutes). Copy it securely.  
5. **Log In with Temporary Password** – Use the temporary password to log into Windows/SSO. You will be prompted to create a new password.  
6. **Create a New Password** – Follow PKC’s password policy:  
   - Minimum 12 characters  
   - At least 1 uppercase, 1 lowercase, 1 digit, and 1 special character (`!@#$%^&*`)  
   - No reuse of the last 5 passwords  
   - Must not contain your name or employee ID.  
7. **Confirm & Save** – Re‑enter the new password, click **Submit**, and log out. Log back in to verify.  

## Post‑Reset Checklist  

- Verify access to critical apps (Outlook, Confluence, GitHub).  
- Update saved credentials in password managers (e.g., LastPass – annual licence cost ₹2.5 L).  
- Inform your line manager that the reset is complete.  

## Common Issues & Troubleshooting  

| Symptom | Likely Cause | Remedy |
|---------|--------------|--------|
| OTP not received | Mobile number not updated | Update mobile in HR portal or contact IT at +91‑80‑9876‑5432. |
| Temporary password expired | Delay >30 min | Generate a new ticket; the system does not allow reuse of expired temps. |
| Account locked after 5 failed attempts | Security lockout | IT will unlock after ticket verification; expect a 2‑hour turnaround on non‑holiday days. |

## Escalation Path  

1. **Level 1** – IT Helpdesk (9 am–6 pm, Mon‑Fri, excluding Indian public holidays such as Republic Day 26 Jan, Independence Day 15 Aug, and Gandhi Jayanti 2 Oct).  
2. **Level 2** – Senior Analyst, Rohan Mehta (r.mehta@pkc.in, +91‑80‑1122‑3344).  
3. **Level 3** – Head of IT, Ananya Singh (a.singh@pkc.in, +91‑80‑5566‑7788).  

For urgent security incidents (e.g., suspected breach), call the 24 × 7 Security Hotline at +91‑80‑9999‑0000.

## Documentation & Auditing  

All password reset tickets are retained for 24 months in the PKC compliance repository. Quarterly audits (Q1 2025, Q2 2025, …) will review reset volumes; average monthly resets in FY 2024‑25 were **≈ 1,850** across both locations, with a total spend on password‑management tools of **₹42.7 crore**.

---  

*For any feedback on this procedure, email it‑process@pkc.in.*