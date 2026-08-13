---
doc_id: co-it-howto-slack-email
doc_class: it_howto
department: company_wide
title: "IT How-To: Setting Up Slack and Email"
contains_pii: false
special_case: null
---

# IT How-To: Setting Up Slack and Email

## Overview  

PKC Technologies uses Slack for instant collaboration and Google Workspace for corporate email. This guide walks every employee—whether at the Bengaluru headquarters or the Austin satellite office—through the end‑to‑end setup, from receiving credentials to joining the relevant channels. The entire process should be completed within **5 business days** of your start date, excluding Indian public holidays (e.g., Republic Day 26 Jan, Independence Day 15 Aug, Gandhi Jayanti 2 Oct).

## Prerequisites  

| Item | Details |
|------|---------|
| Company laptop / desktop | Pre‑installed Windows 11 or macOS 13, latest security patches |
| Internet connection | Minimum 10 Mbps (wired or Wi‑Fi) |
| Personal mobile number | Must be an Indian number (e.g., **+91‑80‑1234‑5678**) for MFA |
| Email address | Assigned by IT (format: `firstname.lastname@pkc.in`) |
| Slack invitation | Sent by HR on the first day of onboarding |

**Cost reference (FY 2025‑26):** Slack Enterprise Grid subscription – **₹12.5 L** per annum for 200 users; Google Workspace – **₹8.3 L** per annum for 250 mailboxes. These figures are for internal budgeting only and are not billed to employees.

## Step‑by‑Step Slack Setup  

1. **Accept the invitation**  
   - Open the welcome email from `hr@pkc.in`. Click **“Join Slack”**.  
   - You will be redirected to `pkc.slack.com`.  

2. **Create your account**  
   - Use your corporate email (`firstname.lastname@pkc.in`).  
   - Set a strong password (minimum 12 characters, mix of upper‑case, lower‑case, numbers, symbols).  

3. **Enable Multi‑Factor Authentication (MFA)**  
   - After logging in, go to **Settings → Security → Two‑factor authentication**.  
   - Choose **SMS** and enter your Indian mobile number (**+91‑80‑xxxx‑xxxx**).  
   - Enter the OTP received and confirm.  

4. **Join mandatory channels**  
   - `#announcements` – company‑wide news (read‑only).  
   - `#it-support` – for technical tickets.  
   - `#project‑<your‑team>` – e.g., `#project‑ai‑core`.  

5. **Configure notifications**  
   - Desktop: **Preferences → Notifications → Highlight words** (add your name).  
   - Mobile: Set **“Do Not Disturb”** from 10 pm to 6 am IST.  

6. **Test connectivity**  
   - Post a short “Hello” in `#it-support`. The bot should reply with a confirmation message.  

> **Tip:** If you encounter “Unable to verify phone number”, contact the IT desk at **+91‑80‑1234‑5678** (ext 212).

## Step‑by‑Step Email Setup  

1. **Access Google Workspace**  
   - Navigate to `mail.pkc.in` or open the Gmail app.  
   - Sign in with `firstname.lastname@pkc.in` and the same password used for Slack.  

2. **Set up MFA (Google Authenticator)**  
   - In Gmail, click the avatar → **Google Account → Security → 2‑Step Verification**.  
   - Choose **Authenticator app** and scan the QR code with the Google Authenticator app on your phone.  

3. **Create a signature**  
   - Settings (gear icon) → **See all settings** → **Signature**.  
   - Use the template:  

   ```
   Regards,
   Firstname Lastname
   Senior Software Engineer | PKC Technologies
   📞 +91‑80‑1234‑5678 | 📧 firstname.lastname@pkc.in
   Bengaluru, India | Austin, USA
   ```  

4. **Add PKC contacts to your address book**  
   - Import `PKC_Contacts.csv` from the IT SharePoint (`\\pkc\it\resources`).  

5. **Configure email forwarding (optional)**  
   - If you use a personal mailbox for alerts, set up forwarding under **Settings → Forwarding and POP/IMAP**.  

6. **Verify delivery**  
   - Send a test mail to `it-support@pkc.in` with subject **“Email Setup Test – [Your Name]”**.  
   - Expect an automated acknowledgment within 2 minutes.  

## Support & Escalation  

- **First‑line:** `it-support@pkc.in` (Slack ticket or email).  
- **Phone:** +91‑80‑1234‑5678 (Mon‑Fri 9 am‑6 pm IST).  
- **Escalation:** If the issue persists beyond 48 hours, contact **Rajesh Kumar, IT Manager** – ext 212, mobile **+91‑80‑9876‑5432**.  

All configurations must be completed before the next **Quarterly Review** on **15 Oct 2026** to ensure compliance with PKC’s security policy.