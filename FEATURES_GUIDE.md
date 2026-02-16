# 🗄️ OracleDBA - Complete Feature Guide

## 📖 Table of Contents

- [Quick Start](#quick-start)
- [Sample Database](#sample-database)
- [Foundation Features](#foundation-features)
- [Storage Management](#storage-management)
- [Data Protection](#data-protection)
- [Security & Access](#security--access)
- [Performance & Tuning](#performance--tuning)
- [High Availability](#high-availability)
- [Advanced Features](#advanced-features)
- [Command Reference](#command-reference)

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba

# Install package
sudo bash install.sh

# Verify installation
oradba --version
```

### Create Your First Database
```bash
# 1. Check system requirements
oradba precheck

# 2. Prepare system
oradba install system

# 3. Install Oracle binaries
oradba install binaries --oracle-zip /path/to/LINUX.X64_193000_db_home.zip

# 4. Create database
oradba database create --sid PRODDB --memory 4096

# 5. Enable protection features
oradba protection archivelog enable
oradba rman configure
oradba rman backup full
```

### Quick Test with Sample Database
```bash
# Create pre-configured test database
oradba sample create

# Test all features
oradba sample test

# View status
oradba sample status

# Connect and explore
sqlplus sample_user/SamplePass123@SAMPLEDB
```

---

## 🧪 Sample Database

**Purpose:** Fully configured Oracle database with sample data for learning and testing all features.

### What You Get:
- ✅ **3 tables** with realistic data (customers, orders, products)
- ✅ **6000+ rows** ready for queries
- ✅ **Indexes** on common query columns
- ✅ **Stored procedures** for testing PL/SQL
- ✅ **ARCHIVELOG mode** enabled
- ✅ **Multiplexed** control files & redo logs
- ✅ **Flashback Database** enabled (24h retention)
- ✅ **RMAN** configured with compression
- ✅ **Security profiles** with password policies
- ✅ **Fast Recovery Area** configured

### Commands

```bash
# Create sample database
oradba sample create

# Show configuration and statistics
oradba sample status

# Test all features
oradba sample test

# Test specific feature
oradba sample test --feature archivelog
oradba sample test --feature rman
oradba sample test --feature flashback

# Get connection info
oradba sample connect

# Remove sample database
oradba sample remove --force
```

### Use Cases

**Learning**: Practice DBA tasks without risking production
```bash
oradba sample create
oradba sample test
# Practice: backup, restore, user management, tuning
```

**Testing**: Validate oradba commands before production use
```bash
oradba sample create
oradba rman backup full
oradba flashback database restore --to-time '10 minutes ago'
```

**Development**: Dev environment with realistic data
```bash
oradba sample create
sqlplus sample_user/SamplePass123@SAMPLEDB
SQL> SELECT * FROM customers WHERE email LIKE '%@example.com';
```

---

## 🏗️ Foundation Features

### System Preparation

**What it does:** Prepares Linux system with all Oracle prerequisites

```bash
# Check system readiness
oradba precheck

# Check specific category
oradba precheck --category system
oradba precheck --category storage
oradba precheck --category network

# Install requirements
oradba install system

# Verify after installation
oradba precheck --category system
```

**Manual verification:**
```bash
# Check kernel parameters
sysctl -a | grep -i sem
sysctl -a | grep -i shm

# Check Oracle user
id oracle

# Check directories
ls -l /u01/app/oracle
```

### Oracle Installation

**What it does:** Installs Oracle 19c binaries

```bash
# Full installation
oradba install full --oracle-zip /path/to/oracle.zip

# Step-by-step
oradba install system              # System prep only
oradba install binaries            # Binaries only

# Verify installation
$ORACLE_HOME/bin/sqlplus -v
ls -l $ORACLE_HOME/bin/sqlplus
```

**What gets installed:**
- Oracle Home: `/u01/app/oracle/product/19.3.0/dbhome_1`
- Binaries: sqlplus, rman, lsnrctl, dbca
- Libraries: libclntsh.so, libocci.so
- Tools: SQL*Plus, RMAN, Data Pump

### Database Creation

**What it does:** Creates Oracle database instance

```bash
# Create database
oradba database create --sid PRODDB --memory 4096 --storage 20GB

# Create with PDB
oradba database create --sid PRODDB --pdb-name PDB1

# Create minimal
oradba database create --sid TESTDB --minimal

# Verify
oradba database status
oradba database list
```

**Test connection:**
```bash
# As SYSDBA
sqlplus / as sysdba
SQL> SELECT instance_name, status FROM v$instance;

# As application user (after user creation)
sqlplus appuser/password@PRODDB
```

---

## 💾 Storage Management

### Tablespaces

**What it does:** Manages logical storage containers

```bash
# Create tablespace
oradba storage tablespace create --name APP_DATA --size 1G --autoextend on --maxsize 10G

# Create index tablespace
oradba storage tablespace create --name APP_INDEX --size 500M

# List tablespaces
oradba storage tablespace list

# Resize tablespace
oradba storage tablespace resize --name APP_DATA --size 5G

# Add datafile
oradba storage tablespace add-datafile --name APP_DATA --size 2G

# Drop tablespace
oradba storage tablespace drop --name APP_DATA --cascade
```

**Monitor space:**
```sql
-- Space usage
SELECT tablespace_name, 
       ROUND(used_space*8192/1024/1024, 2) as used_mb,
       ROUND(tablespace_size*8192/1024/1024, 2) as total_mb,
       ROUND(used_percent, 2) as pct_used
FROM dba_tablespace_usage_metrics;

-- Datafiles
SELECT file_name, tablespace_name, 
       ROUND(bytes/1024/1024, 2) as size_mb,
       autoextensible
FROM dba_data_files
ORDER BY tablespace_name;
```

### Control File Multiplexing

**What it does:** Creates redundant copies of control files

```bash
# Enable multiplexing (3 copies recommended)
oradba storage multiplex controlfile --copies 3

# Verify
oradba storage status controlfiles

# Test
oradba storage test controlfiles
```

**Why:** Control file contains critical database metadata. If lost, database won't start. Multiplexing protects against disk failure.

**Locations:**
- Copy 1: `/u01/app/oracle/oradata/PRODDB/control01.ctl`
- Copy 2: `/u02/app/oracle/oradata/PRODDB/control02.ctl`
- Copy 3: `/u03/app/oracle/oradata/PRODDB/control03.ctl`

### Redo Log Multiplexing

**What it does:** Creates redundant redo log members

```bash
# Enable multiplexing (2 members per group)
oradba storage multiplex redolog --members 2

# Force log switch (for testing)
oradba storage redolog switch

# Verify
oradba storage status redologs

# Show current/active redo
oradba storage redolog current
```

**Why:** Redo logs record all transactions. If redo log is corrupted and not multiplexed, you lose transactions.

**Structure:**
```
Group 1: redo01a.log (200MB) + redo01b.log (200MB)
Group 2: redo02a.log (200MB) + redo02b.log (200MB)
Group 3: redo03a.log (200MB) + redo03b.log (200MB)
```

---

## 🛡️ Data Protection

### Archive Log Mode

**What it does:** Enables continuous backup of redo logs

```bash
# Enable ARCHIVELOG mode
oradba protection archivelog enable

# Disable (NOT RECOMMENDED for production)
oradba protection archivelog disable

# Check status
oradba protection archivelog status

# Test
oradba protection archivelog test
```

**Critical:** Without ARCHIVELOG, you can only restore to last backup. With ARCHIVELOG, you can restore to any point in time.

**Verify:**
```sql
SELECT log_mode FROM v$database;
-- Should show: ARCHIVELOG

ARCHIVE LOG LIST;
-- Shows archive destination and sequence
```

### Fast Recovery Area (FRA)

**What it does:** Manages disk space for backups and recovery files

```bash
# Enable FRA
oradba protection fra enable --size 100G --location /u01/fra

# Check status
oradba protection fra status

# Cleanup old files
oradba protection fra cleanup --older-than 7d

# Monitor space
oradba protection fra monitor
```

**What's stored in FRA:**
- Archive logs
- RMAN backups
- Flashback logs
- Control file autobackups

### RMAN Backup

**What it does:** Backs up database with compression and validation

```bash
# Configure RMAN
oradba rman configure

# Full backup
oradba rman backup full

# Incremental backup (level 1)
oradba rman backup incremental --level 1

# Backup with validation
oradba rman backup full --verify

# List backups
oradba rman list backups

#Restore database
oradba rman restore --to-time '2026-01-15 14:30:00'

# Restore specific tablespace
oradba rman restore --tablespace APP_DATA
```

**RMAN features:**
- ✅ **Compression:** Saves 50-70% disk space
- ✅ **Validation:** Detects corruption during backup
- ✅ **Incremental:** Only backs up changed blocks
- ✅ **Auto-cleanup:** Removes obsolete backups per retention policy

**Recommended schedule:**
```bash
# Daily full backup (night)
0 2 * * * oradba rman backup full --compress

# Hourly incremental (business hours)
0 8-18 * * * oradba rman backup incremental --level 1

# Weekly validation
0 3 * * 0 oradba rman backup full --verify
```

### Flashback Database

**What it does:** Rewinds entire database to previous state

```bash
# Enable Flashback Database
oradba flashback database enable --retention 24h

# Extend retention
oradba flashback database extend --retention 48h

# Restore to previous time
oradba flashback database restore --to-time '2 hours ago'
oradba flashback database restore --to-timestamp '2026-01-15 10:00:00'

# Status
oradba flashback database status
```

**Use cases:**
- Undo bad batch job
- Recover from logical error faster than RMAN
- Test changes then rewind

**Speed:** Minutes vs hours for RMAN restore

### Flashback Table

**What it does:** Restores individual table without affecting other data

```bash
# Restore table to previous state
oradba flashback table restore --table ORDERS --to-time '1 hour ago'

# Query historical data (doesn't change anything)
oradba flashback table query --table CUSTOMERS --as-of '2026-01-15 09:00:00'

# Recover dropped table
oradba flashback table undrop --table INVOICES

# Show what can be recovered
oradba flashback table list-recycle
```

**Limitations:**
- Requires UNDO data (retention period)
- Must enable ROW MOVEMENT on table
- Can't flashback DDL changes

---

## 🔐 Security & Access

### User Management

**What it does:** Creates and manages database users

```bash
# Create user
oradba security user create --name APPUSER --password SecurePass123 --tablespace APP_DATA

# Create with quota
oradba security user create --name DEVUSER --password Dev123 --quota 500M

# List users
oradba security user list

# List application users only
oradba security user list --pattern 'APP%'

# Lock user
oradba security user lock --name APPUSER

# Unlock user
oradba security user unlock --name APPUSER

# Change password
oradba security user password --name APPUSER --new-password NewPass456

# Drop user
oradba security user drop --name APPUSER --cascade
```

**Best practices:**
- ✅ Never use SYS/SYSTEM for applications
- ✅ Create dedicated users per application
- ✅ Set tablespace quotas
- ✅ Apply security profiles

### Privileges & Roles

**What it does:** Controls what users can do

```bash
# Grant system privilege
oradba security grant --user APPUSER --privilege 'CREATE TABLE'
oradba security grant --user APPUSER --privilege 'CREATE VIEW'

# Grant role
oradba security grant --user DEVUSER --role DEVELOPER

# Grant object privilege
oradba security grant --user READONLY --privilege SELECT --on APPUSER.ORDERS

# Revoke
oradba security revoke --user APPUSER --privilege 'DROP TABLE'

# List privileges
oradba security privileges list --user APPUSER
```

**Common roles:**
- `CONNECT`: Login only
- `RESOURCE`: Create tables, procedures
- `DBA`: Full admin (use carefully!)
- Custom roles: Create your own

### Security Profiles

**What it does:** Enforces password policies and resource limits

```bash
# Create security profile
oradba security profile create --name PCI_COMPLIANT \
  --password-life 90 \
  --failed-attempts 3 \
  --lock-time 30m

# Apply to user
oradba security profile apply --name PCI_COMPLIANT --user APPUSER

# List profiles
oradba security profile list

# Show profile details
oradba security profile show --name PCI_COMPLIANT
```

**Profile settings:**
- `PASSWORD_LIFE_TIME`: Days before password expires (90)
- `FAILED_LOGIN_ATTEMPTS`: Lockout after N failures (3)
- `PASSWORD_LOCK_TIME`: How long locked (30 minutes or 1 day)
- `PASSWORD_REUSE_TIME`: Can't reuse password for N days (180)
- `PASSWORD_REUSE_MAX`: Must change N times before reuse (5)

### Audit Trail

**What it does:** Tracks who did what and when

```bash
# Enable auditing
oradba security audit enable --actions 'LOGIN,LOGOFF,DDL'

# Enable for specific users
oradba security audit enable --users 'APPUSER,DEVUSER' --actions 'DELETE,UPDATE'

# View audit records
oradba security audit show --last 24h
oradba security audit show --user APPUSER
oradba security audit show --action DROP

# Export audit log
oradba security audit export --format csv --output /tmp/audit.csv

# Disable auditing
oradba security audit disable
```

**What's audited:**
- User logins/logoffs
- Schema changes (CREATE, ALTER, DROP)
- Grant/revoke privileges
- Data modifications (optional)
- Failed login attempts

---

## ⚡ Performance & Tuning

### AWR Report

**What it does:** Generates performance diagnostic report

```bash
# Generate report for last hour
oradba tuning awr generate --last 1h

# Generate for specific time range
oradba tuning awr generate --from '2026-01-15 09:00' --to '2026-01-15 10:00'

# Compare two periods
oradba tuning awr compare --baseline yesterday --current today

# Create manual snapshot
oradba tuning awr snapshot create

# List snapshots
oradba tuning awr snapshot list
```

**What AWR shows:**
- Top 10 SQL by CPU, elapsed time, executions
- Wait events (what database is waiting for)
- I/O statistics
- Memory usage
- Cache hit ratios

**How to read AWR:**
1. Look at "Top 10 SQL" section
2. Check wait events (DB file sequential read = slow disk)
3. Review load profile (transactions/second)
4. Check SGA hit ratios (>95% is good)

### SQL Tuning

**What it does:** Analyzes and optimizes slow queries

```bash
# Analyze slow SQL by ID
oradba tuning sql analyze --sql-id 'abc123def456'

# Auto-tune top 10 slow queries
oradba tuning sql auto --top 10

# Show recommendations
oradba tuning sql recommendations --task-name 'TUNE_TASK_001'

# Implement recommendations
oradba tuning sql implement --task-name 'TUNE_TASK_001'

# Analyze query text
oradba tuning sql analyze --sql-text "SELECT * FROM orders WHERE order_date > SYSDATE-30"
```

**What SQL Tuning Advisor suggests:**
- Missing indexes
- Better execution plan
- SQL rewrite
- Statistics gathering
- Parallel execution

### Statistics Gathering

**What it does:** Updates optimizer statistics for better query plans

```bash
# Gather for specific schema
oradba tuning stats gather --schema APPUSER

# Gather for specific table
oradba tuning stats gather --table APPUSER.ORDERS

# Gather for all schemas
oradba tuning stats gather --all

# Enable automatic statistics (recommended)
oradba tuning stats auto enable

# Show current statistics
oradba tuning stats show --table APPUSER.ORDERS
```

**When to gather stats:**
- After large data loads
- After major DELETE operations
- When queries suddenly become slow
- Daily for volatile tables (automatic job handles this)

**What statistics include:**
- Number of rows
- Number of distinct values per column
- Data distribution (histogram)
- Index selectivity

---

## 🔄 High Availability

### Data Guard

**What it does:** Maintains synchronized standby database for disaster recovery

```bash
# Setup Data Guard (primary + standby)
oradba dataguard setup --primary 10.0.0.1 --standby 10.0.0.2 --sync realtime

# Check status
oradba dataguard status

# Show lag
oradba dataguard lag

# Switchover (planned)
oradba dataguard switchover

# Failover (emergency)
oradba dataguard failover --force

# Enable/disable apply
oradba dataguard apply start
oradba dataguard apply stop
```

**Modes:**
- **SYNC**: Zero data loss (for local standby)
- **ASYNC**: Better performance (for remote standby)
- **REALTIME**: Apply redo as it arrives

**Use cases:**
- Geographic disaster recovery
- Planned maintenance (switchover)
- Fast recovery from primary failure

### Listener Management

**What it does:** Manages network access to database

```bash
# Start listener
oradba database listener start

# Stop listener
oradba database listener stop

# Status
oradba database listener status

# Reload configuration
oradba database listener reload

# Show services
oradba database listener services
```

**Test connectivity:**
```bash
# From local machine
tnsping PRODDB

# From remote machine
sqlplus appuser/password@10.0.0.1:1521/PRODDB
```

### Cluster Management

**What it does:** Manages multiple database nodes

```bash
# Add database node
oradba cluster add-node --name node1 --ip 10.0.0.10 --role database --sid PRODDB1

# Add NFS server
oradba cluster add-nfs --name nfs1 --ip 10.0.0.20 --exports /nfs/backup,/nfs/fra

# List all nodes
oradba cluster list

# Show node details
oradba cluster show node1

# Deploy oradba to node
oradba cluster deploy node1

# Execute command on node
oradba cluster ssh node1 "df -h"

# Remove node
oradba cluster remove-node node2

# Export inventory
oradba cluster export --format ansible
```

**Configuration stored:** `~/.oracledba/cluster.yaml`  
**SSH keys stored:** `~/.oracledba/ssh_keys/`

---

## 🚀 Advanced Features

### Pluggable Databases (PDB)

**What it does:** Manages multiple databases in single instance

```bash
# Create PDB
oradba pdb create --name SALESDB --admin salesadmin

# Open PDB
oradba pdb open --name SALESDB

# Close PDB
oradba pdb close --name SALESDB

# Drop PDB
oradba pdb drop --name SALESDB

# Clone PDB
oradba pdb clone --source SALESDB --target SALESDB_DEV

# List PDBs
oradba pdb list

# Show PDB details
oradba pdb show --name SALESDB
```

**Connect to PDB:**
```bash
sqlplus appuser/password@localhost:1521/SALESDB
```

**Benefits:**
- Consolidate multiple databases
- Faster cloning
- Easier patching (patch CDB once)
- Resource isolation

### Data Pump

**What it does:** High-speed data export/import

```bash
# Export schema
oradba datapump export --schema APPUSER --file backup.dmp

# Export specific tables
oradba datapump export --tables APPUSER.ORDERS,APPUSER.CUSTOMERS --file tables.dmp

# Import
oradba datapump import --file backup.dmp

# Import with remap
oradba datapump import --file backup.dmp --remap APPUSER:NEWUSER

# Network import (no .dmp file)
oradba datapump network-import --source-db PRODDB --target-db DEVDB --schemas APPUSER

# Parallel export
oradba datapump export --schema APPUSER --parallel 4 --compress
```

**Use cases:**
- Migrate data between databases
- Refresh DEV from PROD
- Logical backups
- Clone specific schemas

---

## 📚 Command Reference

### Help System

```bash
# Show all features
oradba help features

# Get help on specific feature
oradba help archivelog
oradba help rman-backup
oradba help flashback-table

# Show production workflow
oradba help workflow

# Search features
oradba help search backup
oradba help search performance

# Quick reference (one-liners)
oradba help quick
```

### Testing Commands

```bash
# Run all prechecks
oradba precheck

# Test specific category
oradba precheck --category system
oradba precheck --category storage
oradba precheck --category oracle

# Run all tests
oradba test --all

# Test specific features
oradba test --category backup
oradba test --category security

# Generate test report
oradba test --report /tmp/test-report.html
```

### Common Workflows

**New Production Database:**
```bash
oradba precheck && \
oradba install full --oracle-zip /path/to/oracle.zip && \
oradba database create --sid PRODDB --memory 8192 && \
oradba protection archivelog enable && \
oradba storage multiplex controlfile --copies 3 && \
oradba storage multiplex redolog --members 2 && \
oradba flashback database enable --retention 24h && \
oradba rman configure && \
oradba rman backup full
```

**Quick Test Environment:**
```bash
oradba sample create && \
oradba sample test && \
oradba sample connect
```

**Daily Maintenance:**
```bash
# Check database health
oradba database status

# Run backup
oradba rman backup incremental --level 1

# Check storage
oradba storage status

# Review AWR
oradba tuning awr generate --last 24h
```

---

## 💡 Tips & Best Practices

### Security

- ✅ **Never share SYS/SYSTEM passwords**
- ✅ **Create dedicated users per application**
- ✅ **Apply security profiles to all users**
- ✅ **Enable auditing for compliance**
- ✅ **Rotate passwords every 90 days**

### Protection

- ✅ **Always enable ARCHIVELOG mode** for production
- ✅ **Multiplex control files** (3 copies minimum)
- ✅ **Multiplex redo logs** (2 members per group)
- ✅ **Daily full backup** + hourly incrementals
- ✅ **Test restores monthly**

### Performance

- ✅ **Gather statistics** after data loads
- ✅ **Review AWR weekly** for trends
- ✅ **Monitor tablespace usage** (alert at 90%)
- ✅ **Keep redo logs on fast disks** (SSD)
- ✅ **Separate data and index tablespaces**

### High Availability

- ✅ **Setup Data Guard** for mission-critical databases
- ✅ **Test switchover quarterly**
- ✅ **Monitor standby lag** (should be < 1 minute)
- ✅ **Document failover procedures**
- ✅ **Use cluster management** for multi-node setups

---

## 🆘 Troubleshooting

### Database Won't Start

```bash
# Check alert log
tail -100 $ORACLE_BASE/diag/rdbms/*/PRODDB/trace/alert_PRODDB.log

# Try mounting
sqlplus / as sysdba
SQL> STARTUP MOUNT;
SQL> SELECT * FROM v$database;

# Check control files
SQL> SELECT name FROM v$controlfile;

# Restore control file if corrupted
oradba rman restore controlfile
```

### Out of Space

```bash
# Check tablespace usage
oradba storage tablespace list

# Add datafile
oradba storage tablespace add-datafile --name APP_DATA --size 5G

# Cleanup FRA
oradba protection fra cleanup --older-than 7d

# Delete obsolete backups
oradba rman cleanup --obsolete
```

### Slow Queries

```bash
# Generate AWR report
oradba tuning awr generate --last 1h

# Analyze slow SQL
oradba tuning sql analyze --sql-id '<from_awr_report>'

# Gather statistics
oradba tuning stats gather --schema APPUSER

# Check execution plan
sqlplus appuser/password@PRODDB
SQL> SET AUTOTRACE ON
SQL> SELECT * FROM orders WHERE order_date > SYSDATE-30;
```

### Connection Issues

```bash
# Check listener
oradba database listener status

# Restart listener
oradba database listener stop
oradba database listener start

# Test tnsping
tnsping PRODDB

# Check firewall
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=1521/tcp --permanent
```

---

## 📞 Support

- **Documentation:** [https://github.com/ELMRABET-Abdelali/oracledba](https://github.com/ELMRABET-Abdelali/oracledba)
- **Issues:** Open GitHub issue with `oradba --version` and error output
- **Feature Requests:** Submit via GitHub
- **Help:** Use `oradba help features` for complete reference

---

**Remember:** Always test on sample database before production!

```bash
oradba sample create && oradba sample test
```
