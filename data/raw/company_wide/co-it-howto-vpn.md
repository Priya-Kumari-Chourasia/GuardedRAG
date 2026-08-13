---
doc_id: co-it-howto-vpn
doc_class: it_howto
department: company_wide
title: "IT How-To: VPN Setup Guide"
contains_pii: false
special_case: null
---

# IT How-To: VPN Setup Guide

## Overview  
This guide outlines the end‑to‑end process for provisioning a site‑to‑site VPN between PKC Technologies’ Bengaluru headquarters (PKC‑B) and the Austin satellite office (PKC‑A). The solution uses Cisco ASA 5506‑X firewalls with IPSec tunnels, managed centrally via the PKC Network Operations Centre (NOC). The annual VPN licence cost is **₹12.5 L**, and the one‑time hardware refresh budget is **₹3.2 L** (approved in FY 2024‑25).  

## Prerequisites  

| Item | Details | Owner | Cost |
|------|---------|-------|------|
| Firewall firmware | Cisco ASA 9.12(4) or later | Infra Team Lead – Ananya Rao | – |
| VPN licence | 2‑site IPSec licence (perpetual) | PKC‑B Finance – Rohan Mehta | **₹12.5 L** |
| IP address plan | Public /31 for each tunnel (e.g., 203.0.113.10/31 – Bengaluru, 203.0.113.12/31 – Austin) | Network Architect – Sandeep Patel | – |
| User credentials | Pre‑shared key (PSK) – 32‑char alphanumeric, rotated every 180 days | Security Ops – Priya Nair | – |
| Maintenance window | 02:00‑04:00 IST on non‑working days (avoid Republic Day 26‑01‑2025, Independence Day 15‑08‑2025, Diwali 01‑11‑2025) | NOC Scheduler – Vikram Singh | – |

## Step‑by‑Step Configuration  

1. **Log into the ASA GUI** (Bengaluru: `https://10.0.0.1` – admin: `pkc_vpnadmin`).  
2. **Create the tunnel interface**:  
   ```  
   interface Tunnel0  
     ip address 203.0.113.10 255.255.255.254  
     tunnel source interface GigabitEthernet0/0  
     tunnel destination 203.0.113.12  
   ```  
3. **Define the IPSec policy**:  
   - Encryption: AES‑256  
   - Integrity: SHA‑256  
   - DH Group: 14  
   - Lifetime: 86400 seconds  
4. **Apply the pre‑shared key**: `PKC@2025!Secure#` (store in the encrypted vault).  
5. **Configure the remote ASA (Austin)** with the mirrored settings (Tunnel0 IP = 203.0.113.12).  
6. **Create access‑list** permitting only corporate subnets (Bengaluru 10.10.0.0/16 ↔ Austin 172.16.0.0/16).  
7. **Commit and save** the configuration: `write memory`.  

## Testing & Validation  

- From a Bengaluru workstation (`10.10.5.23`), ping `172.16.3.45` (Austin). Expect < 30 ms latency.  
- Run `show vpn-sessiondb detail anyconnect` on both firewalls to verify tunnel status = **UP**.  
- Capture logs for 5 minutes using `debug crypto ipsec` and archive to the NOC ticket **PKC‑VPN‑2025‑001**.  

## Common Issues & Fixes  

| Symptom | Likely Cause | Remedy |
|---------|--------------|--------|
| Tunnel flaps every 10 min | Mismatched DH group | Re‑apply DH‑14 on both ends |
| No traffic after PSK change | PSK not updated on remote ASA | Re‑enter PSK and restart tunnel |
| High latency (> 100 ms) | ISP congestion on 203.0.113.0/30 | Open a ticket with ISP (contact: +91‑80‑1234‑5678) |

## Support & Escalation  

- **First‑line**: NOC – Phone: +91‑80‑1234‑5678, Email: noc@pkc.in (24 × 7).  
- **Second‑line**: Network Security Lead – Ananya Rao – Phone: +91‑80‑9876‑5432.  
- **Escalation**: Head of Infrastructure – Ramesh Kumar – Phone: +91‑80‑5555‑1111 (available during Indian business hours, 09:00‑18:00 IST).  

All changes must be logged in the PKC Change Management System (CMDB) with a minimum **₹1.8 crore** annual security spend allocation for monitoring and incident response.  

---  

*Document version: 1.3 (updated 12‑03‑2025). For any deviations from this procedure, raise a formal change request before implementation.*