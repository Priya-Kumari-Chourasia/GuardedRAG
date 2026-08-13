---
doc_id: eng-runbook-db-backup
doc_class: runbook
department: engineering
title: "Runbook — Database Backup and Restore"
contains_pii: false
special_case: null
---

# Runbook — Database Backup and Restore

## Overview  
This runbook describes the end‑to‑end process for backing up and restoring the primary PostgreSQL clusters that host PKC Technologies’ core SaaS platform (PKC‑Core). The procedures are executed daily from the Bengaluru data centre (DC‑B) and mirrored to the Austin satellite site (DC‑A) for disaster‑recovery (DR). All timestamps are in IST unless otherwise noted.

## Scope  
- Production databases: `pkc_core_main`, `pkc_core_analytics`  
- Backup storage: NetApp AFF‑A300 (Bengaluru) and AWS S3 (US‑East‑1) for off‑site copies  
- Restore targets: DR‑ready standby cluster in Austin and on‑prem test cluster for sanity checks  

## Prerequisites  
| Item | Details |
|------|---------|
| Backup user | `bk_user` (role: `pg_backup`) |
| SSH key | Stored in Vault under `pkc/ssh/backup_key` |
| Disk space | Minimum 2.5 TB free on `/mnt/backup` (≈ ₹12.5L annual storage cost) |
| Network | 10 Gbps link between DC‑B and DC‑A, latency < 15 ms |
| Maintenance window | Daily 02:00 – 03:00 IST (except on **Republic Day (26 Jan)**, **Independence Day (15 Aug)**, **Diwali (15 Nov)**) |
| Personnel | Backup Engineer – **Ananya Rao** (📞 +91‑98765 43210) ; DR Lead – **Rohit Mehta** (📞 +91‑91234 56789) |

## Daily Backup Procedure  
1. **Login** to the backup host (`bk01.bengaluru.pkc.in`) using the Vault‑managed SSH key.  
2. **Run** the scheduled cron job `pg_dumpall -U bk_user -f /mnt/backup/pkc_core_$(date +%F).sql.gz`.  
3. **Verify** file size > 500 GB and checksum (`sha256sum`) matches the log entry.  
4. **Copy** the archive to the off‑site bucket:  
   ```bash
   aws s3 cp /mnt/backup/pkc_core_$(date +%F).sql.gz s3://pkc-dr-backups/$(date +%F)/ --storage-class GLACIER
   ```  
5. **Update** the backup manifest (`/opt/pkc/backup/manifest.yml`) with timestamp, size, and checksum.  
6. **Notify** the on‑call engineer via Slack channel `#pkc-db-backup` and email `backup@pkc.in`.  

## Restore Procedure (Production Failure)  
1. **Assess** the incident; if the primary cluster is unrecoverable, trigger DR.  
2. **Spin up** the standby cluster in Austin (`dr01.austin.pkc.com`).  
3. **Pull** the latest backup from S3:  
   ```bash
   aws s3 cp s3://pkc-dr-backups/$(date -d "yesterday" +%F)/pkc_core_$(date -d "yesterday" +%F).sql.gz /tmp/
   ```  
4. **Restore** using `pg_restore`:  
   ```bash
   gunzip -c /tmp/pkc_core_$(date -d "yesterday" +%F).sql.gz | psql -U bk_user -d pkc_core_main
   ```  
5. **Run** post‑restore health checks (connection pool, replication lag < 5 s).  
6. **Switch** DNS CNAME `db.pkc.in` to point to the Austin endpoint (`dr01.austin.pkc.com`).  

## Validation & Post‑Restore Checks  
- Execute `SELECT count(*) FROM users;` on both schemas; counts must match pre‑failure snapshot.  
- Run the automated test suite (`./run_integration_tests.sh`) – must pass ≥ 98 % of 1,200 test cases.  
- Log results in the incident ticket (Jira ID: **PKC‑DB‑REST‑####**).  

## Escalation Matrix  
| Severity | Owner | Contact | SLA |
|----------|-------|---------|-----|
| P1 – Full outage | DR Lead – Rohit Mehta | +91‑91234 56789 | 30 min |
| P2 – Partial degradation | Backup Engineer – Ananya Rao | +91‑98765 43210 | 1 hr |
| P3 – Minor issue | Support Engineer – Kiran Patel | +91‑99887 66554 | 4 hr |

If the issue persists beyond SLA, involve the **Head of Engineering** – **Neha Singh** (📞 +91‑90011 22334).  

## References  
- PKC‑SEC‑001: Data Encryption Policy (AES‑256)  
- PKC‑OPS‑007: Disaster‑Recovery Runbook (Version 3.2, last updated 12 Mar 2024)  
- NetApp AFF‑A300 Maintenance Schedule (available on Confluence)  

---  
*Document version: 1.4 – Effective 01 Oct 2024*