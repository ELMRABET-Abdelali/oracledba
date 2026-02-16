#!/usr/bin/env python3
"""
Comprehensive Help System
Complete documentation for all Oracle features and oradba commands
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.columns import Columns

console = Console()


FEATURE_CATEGORIES = {
    "foundation": {
        "name": "Foundation",
        "icon": "🏗️",
        "description": "System preparation, installation, and database creation"
    },
    "storage": {
        "name": "Storage Management",
        "icon": "💾",
        "description": "Tablespaces, datafiles, and disk management"
    },
    "protection": {
        "name": "Data Protection",
        "icon": "🛡️",
        "description": "Backup, recovery, and data safety features"
    },
    "security": {
        "name": "Security & Access",
        "icon": "🔐",
        "description": "Users, roles, privileges, and authentication"
    },
    "performance": {
        "name": "Performance & Tuning",
        "icon": "⚡",
        "description": "Optimization, monitoring, and diagnostics"
    },
    "availability": {
        "name": "High Availability",
        "icon": "🔄",
        "description": "RAC, Data Guard, and cluster management"
    },
    "advanced": {
        "name": "Advanced Features",
        "icon": "🚀",
        "description": "Multitenant, ASM, and modern capabilities"
    }
}


FEATURES = {
    # ==================== FOUNDATION ====================
    "system-prep": {
        "category": "foundation",
        "name": "System Preparation",
        "description": "Prepare Linux system with required packages, kernel parameters, and Oracle user",
        "commands": {
            "check": "oradba precheck --category system",
            "install": "oradba install system",
            "test": "oradba precheck --category system --fix"
        },
        "what_it_does": "Configures OS prerequisites: installs required packages (libnsl, libaio), sets kernel parameters (shmmax, shmall), creates oracle user/groups, and sets up directory structure",
        "when_to_use": "First step before any Oracle installation",
        "example": "oradba install system --config config.yaml"
    },
    
    "oracle-install": {
        "category": "foundation",
        "name": "Oracle Binary Installation",
        "description": "Install Oracle 19c database software (binaries only, no database creation)",
        "commands": {
            "install": "oradba install binaries --oracle-zip /path/to/LINUX.X64_193000_db_home.zip",
            "verify": "oradba precheck --category oracle",
            "test": "$ORACLE_HOME/bin/sqlplus -v"
        },
        "what_it_does": "Extracts Oracle software, runs runInstaller in silent mode, executes root.sh, and validates ORACLE_HOME",
        "when_to_use": "After system preparation, before creating databases",
        "example": "oradba install binaries --oracle-home /u01/app/oracle/product/19.3.0/dbhome_1"
    },
    
    "database-create": {
        "category": "foundation",
        "name": "Database Creation",
        "description": "Create new Oracle database instance with DBCA",
        "commands": {
            "create": "oradba database create --sid PRODDB --pdb-name PDB1",
            "list": "oradba database list",
            "status": "oradba database status --sid PRODDB"
        },
        "what_it_does": "Creates CDB (Container Database) with optional PDB, configures listener, sets up initial tablespaces (SYSTEM, SYSAUX, TEMP, UNDO)",
        "when_to_use": "After Oracle binaries are installed",
        "example": "oradba database create --sid PRODDB --memory 2048 --storage 10GB"
    },
    
    "sample-db": {
        "category": "foundation",
        "name": "Sample Database",
        "description": "Create fully-configured test database with sample data for learning",
        "commands": {
            "create": "oradba sample create",
            "status": "oradba sample status",
            "test": "oradba sample test",
            "remove": "oradba sample remove"
        },
        "what_it_does": "Creates SAMPLEDB with: customers/orders/products tables (6000+ rows), indexes, stored procedures, ARCHIVELOG mode, multiplexed files, security profiles",
        "when_to_use": "For testing oradba features without risking production",
        "example": "oradba sample create && oradba sample test"
    },
    
    # ==================== STORAGE ====================
    "tablespaces": {
        "category": "storage",
        "name": "Tablespace Management",
        "description": "Create and manage logical storage containers for database objects",
        "commands": {
            "create": "oradba storage tablespace create --name DATA01 --size 500M",
            "list": "oradba storage tablespace list",
            "resize": "oradba storage tablespace resize --name DATA01 --size 1G",
            "drop": "oradba storage tablespace drop --name DATA01"
        },
        "what_it_does": "Creates logical storage units with AUTOEXTEND, manages datafiles, monitors space usage, handles OMF (Oracle Managed Files)",
        "when_to_use": "To organize data by application, separate indexes from tables, or isolate user data",
        "example": "oradba storage tablespace create --name APP_DATA --size 1G --autoextend on --maxsize 10G"
    },
    
    "controlfile-multiplex": {
        "category": "storage",
        "name": "Control File Multiplexing",
        "description": "Create redundant copies of control files for fault tolerance",
        "commands": {
            "enable": "oradba storage multiplex controlfile --copies 3",
            "status": "oradba storage status controlfiles",
            "test": "oradba storage test controlfiles"
        },
        "what_it_does": "Creates 2-3 copies of the control file (database metadata) on different disks. If one fails, database continues using others",
        "when_to_use": "Critical for production databases - protects against disk failure",
        "example": "oradba storage multiplex controlfile --locations /u01,/u02,/u03"
    },
    
    "redolog-multiplex": {
        "category": "storage",
        "name": "Redo Log Multiplexing",
        "description": "Create redundant redo log members for transaction safety",
        "commands": {
            "enable": "oradba storage multiplex redolog --members 2",
            "status": "oradba storage status redologs",
            "switch": "oradba storage redolog switch",
            "test": "oradba storage test redologs"
        },
        "what_it_does": "Adds second member to each redo log group. Oracle writes to all members simultaneously. Protects transaction log from corruption",
        "when_to_use": "Essential for any production database to prevent transaction loss",
        "example": "oradba storage multiplex redolog --groups 1,2,3 --location /u02/oradata"
    },
    
    # ==================== PROTECTION ====================
    "archivelog": {
        "category": "protection",
        "name": "Archive Log Mode",
        "description": "Enable continuous archiving of redo logs for point-in-time recovery",
        "commands": {
            "enable": "oradba protection archivelog enable",
            "disable": "oradba protection archivelog disable",
            "status": "oradba protection archivelog status",
            "test": "oradba protection archivelog test"
        },
        "what_it_does": "Archives filled redo logs before reuse. Allows restoration to any point in time (not just last backup). Required for Data Guard",
        "when_to_use": "MANDATORY for production - without it, you can only restore to last backup",
        "example": "oradba protection archivelog enable --dest /u01/archive"
    },
    
    "fra": {
        "category": "protection",
        "name": "Fast Recovery Area",
        "description": "Centralized storage for backups, archivelogs, and flashback logs",
        "commands": {
            "enable": "oradba protection fra enable --size 50G",
            "status": "oradba protection fra status",
            "cleanup": "oradba protection fra cleanup --older-than 7d"
        },
        "what_it_does": "Automatic disk space management for recovery files. Auto-deletes obsolete backups when space needed",
        "when_to_use": "Recommended for all databases with RMAN backup strategy",
        "example": "oradba protection fra enable --location /u01/fra --size 100G"
    },
    
    "rman-backup": {
        "category": "protection",
        "name": "RMAN Backup",
        "description": "Oracle Recovery Manager - automated backup and recovery tool",
        "commands": {
            "configure": "oradba rman configure",
            "backup-full": "oradba rman backup full",
            "backup-incremental": "oradba rman backup incremental --level 1",
            "list": "oradba rman list backups",
            "restore": "oradba rman restore --to-time '2026-01-15 14:30:00'"
        },
        "what_it_does": "Creates compressed backups, validates data integrity, manages backup retention, auto-removes obsolete backups",
        "when_to_use": "Daily full backups + hourly incrementals for production databases",
        "example": "oradba rman backup full --compress --verify && oradba rman list backups"
    },
    
    "flashback-database": {
        "category": "protection",
        "name": "Flashback Database",
        "description": "Rewind entire database to previous point in time (like UNDO for whole DB)",
        "commands": {
            "enable": "oradba flashback database enable --retention 24h",
            "disable": "oradba flashback database disable",
            "restore": "oradba flashback database restore --to-time '2026-01-15 10:00:00'",
            "status": "oradba flashback database status"
        },
        "what_it_does": "Keeps 'before images' of changed blocks. Can rewind database in minutes (vs hours for RMAN restore)",
        "when_to_use": "When you need fast recovery from logical errors (bad batch job, wrong UPDATE)",
        "example": "oradba flashback database enable --retention 48h"
    },
    
    "flashback-table": {
        "category": "protection",
        "name": "Flashback Table",
        "description": "Restore individual table to previous state without affecting other data",
        "commands": {
            "restore": "oradba flashback table restore --table ORDERS --to-time '10 minutes ago'",
            "query": "oradba flashback table query --table ORDERS --as-of '1 hour ago'",
            "drop-recover": "oradba flashback table undrop --table CUSTOMERS"
        },
        "what_it_does": "Uses UNDO data to restore table row-by-row. Can query historical data. Recovers dropped tables from Recycle Bin",
        "when_to_use": "Accidental DELETE/UPDATE on single table, or need to see data from 1 hour ago",
        "example": "oradba flashback table restore --table ORDERS --to-timestamp '2026-01-15 14:00:00'"
    },
    
    # ==================== SECURITY ====================
    "user-create": {
        "category": "security",
        "name": "User Creation",
        "description": "Create database users with tablespace quotas and authentication",
        "commands": {
            "create": "oradba security user create --name APPUSER --password SecurePass123",
            "list": "oradba security user list",
            "lock": "oradba security user lock --name APPUSER",
            "unlock": "oradba security user unlock --name APPUSER",
            "drop": "oradba security user drop --name APPUSER"
        },
        "what_it_does": "Creates schema owner with password, assigns default tablespace, sets quotas, applies security profiles",
        "when_to_use": "Never give SYS/SYSTEM passwords to apps. Create dedicated users with minimal privileges",
        "example": "oradba security user create --name HRUSER --tablespace HR_DATA --quota 1G"
    },
    
    "privileges": {
        "category": "security",
        "name": "Privilege Management",
        "description": "Grant/revoke system and object privileges to users and roles",
        "commands": {
            "grant": "oradba security grant --user APPUSER --privilege 'CREATE TABLE'",
            "revoke": "oradba security revoke --user APPUSER --privilege 'DROP TABLE'",
            "list": "oradba security privileges list --user APPUSER"
        },
        "what_it_does": "Controls what users can do: CREATE SESSION (login), CREATE TABLE, SELECT on specific tables, DBA role",
        "when_to_use": "Apply principle of least privilege - only grant what's needed",
        "example": "oradba security grant --user DEVUSER --role DEVELOPER"
    },
    
    "profiles": {
        "category": "security",
        "name": "Security Profiles",
        "description": "Password policies and resource limits for users",
        "commands": {
            "create": "oradba security profile create --name SECURE_POLICY",
            "apply": "oradba security profile apply --name SECURE_POLICY --user APPUSER",
            "list": "oradba security profile list"
        },
        "what_it_does": "Enforces: password complexity, expiration (90 days), lockout after 3 failed attempts, reuse restrictions",
        "when_to_use": "Compliance requirement for PCI-DSS, GDPR, SOX audits",
        "example": "oradba security profile create --name PCI_COMPLIANT --password-life 90 --failed-attempts 3"
    },
    
    "audit": {
        "category": "security",
        "name": "Audit Trail",
        "description": "Track who did what and when in the database",
        "commands": {
            "enable": "oradba security audit enable --actions 'LOGIN,LOGOFF,DDL'",
            "disable": "oradba security audit disable",
            "show": "oradba security audit show --last 24h",
            "export": "oradba security audit export --format csv"
        },
        "what_it_does": "Logs database actions to audit trail: connections, schema changes, data access. Can't be disabled by users",
        "when_to_use": "Track suspicious activity, prove compliance, forensics after security incident",
        "example": "oradba security audit enable --users PROD_ADMIN --actions 'GRANT,DROP'"
    },
    
    # ==================== PERFORMANCE ====================
    "awr-report": {
        "category": "performance",
        "name": "AWR Report",
        "description": "Automatic Workload Repository - performance diagnosis report",
        "commands": {
            "generate": "oradba tuning awr generate --last 1h",
            "compare": "oradba tuning awr compare --from yesterday --to today",
            "snapshot": "oradba tuning awr snapshot create"
        },
        "what_it_does": "Captures database performance snapshots every hour. Shows: top SQL,  wait events, I/O stats, memory usage",
        "when_to_use": "When users complain 'database is slow' - AWR shows what changed",
        "example": "oradba tuning awr generate --from '2026-01-15 09:00' --to '2026-01-15 10:00'"
    },
    
    "sql-tuning": {
        "category": "performance",
        "name": "SQL Tuning Advisor",
        "description": "Automatic SQL performance analysis and recommendations",
        "commands": {
            "analyze": "oradba tuning sql analyze --sql-id 'abc123def456'",
            "auto": "oradba tuning sql auto --top 10",
            "implement": "oradba tuning sql implement --task-name 'TUNE_TASK_001'"
        },
        "what_it_does": "Analyzes slow queries, suggests: missing indexes, better execution plans, SQL rewrites, statistics gathering",
        "when_to_use": "Specific query is slow and you want Oracle's AI to suggest fixes",
        "example": "oradba tuning sql analyze --sql-text 'SELECT * FROM orders WHERE order_date > SYSDATE-30'"
    },
    
    "stats-gather": {
        "category": "performance",
        "name": "Statistics Gathering",
        "description": "Collect table/index statistics for query optimizer",
        "commands": {
            "gather": "oradba tuning stats gather --schema APPUSER",
            "auto-enable": "oradba tuning stats auto enable",
            "show": "oradba tuning stats show --table ORDERS"
        },
        "what_it_does": "Tells optimizer: how many rows in table, data distribution, index selectivity. Bad stats = bad execution plans",
        "when_to_use": "After large data loads, or when queries suddenly become slow",
        "example": "oradba tuning stats gather --schema APPUSER --tables ORDERS,CUSTOMERS"
    },
    
    # ==================== HIGH AVAILABILITY ====================
    "dataguard": {
        "category": "availability",
        "name": "Data Guard",
        "description": "Physical standby database for disaster recovery",
        "commands": {
            "setup": "oradba dataguard setup --primary 10.0.0.1 --standby 10.0.0.2",
            "status": "oradba dataguard status",
            "switchover": "oradba dataguard switchover",
            "failover": "oradba dataguard failover --force"
        },
        "what_it_does": "Maintains synchronized copy of database on different server. If primary fails, standby becomes primary in minutes",
        "when_to_use": "Mission-critical databases needing 99.99% uptime, geographic disaster recovery",
        "example": "oradba dataguard setup --standby-host standby-server --sync-mode realtime"
    },
    
    "listener": {
        "category": "availability",
        "name": "Listener Management",
        "description": "Network service that accepts client connections",
        "commands": {
            "start": "oradba database listener start",
            "stop": "oradba database listener stop",
            "status": "oradba database listener status",
            "reload": "oradba database listener reload"
        },
        "what_it_does": "Listens on port 1521 (default), routes connections to correct database instance, handles load balancing for RAC",
        "when_to_use": "Must be running for any remote database connections",
        "example": "oradba database listener start && oradba database listener status"
    },
    
    "cluster": {
        "category": "availability",
        "name": "Cluster Management",
        "description": "Manage multiple Oracle nodes and NFS servers",
        "commands": {
            "add-node": "oradba cluster add-node --name node1 --ip 10.0.0.1 --role database",
            "remove-node": "oradba cluster remove-node --name node2",
            "list": "oradba cluster list",
            "deploy": "oradba cluster deploy node1",
            "ssh": "oradba cluster ssh node1 'uptime'"
        },
        "what_it_does": "Centralized management of multi-node architecture: tracks nodes, SSH keys, NFS mounts, enables remote deployment",
        "when_to_use": "Managing 2+ database servers, NFS shared storage, or preparing for RAC",
        "example": "oradba cluster add-node --name dbnode1 --ip 10.0.0.10 --sid PRODDB1"
    },
    
    # ==================== ADVANCED ====================
    "pdb-management": {
        "category": "advanced",
        "name": "Pluggable Databases",
        "description": "Create and manage PDBs in multitenant architecture",
        "commands": {
            "create": "oradba pdb create --name SALESDB",
            "open": "oradba pdb open --name SALESDB",
            "close": "oradba pdb close --name SALESDB",
            "drop": "oradba pdb drop --name SALESDB",
            "clone": "oradba pdb clone --source SALESDB --target SALESDB_DEV"
        },
        "what_it_does": "Consolidate multiple databases into single CDB. Each PDB looks like standalone DB but shares memory/processes",
        "when_to_use": "Consolidate 10 small databases into 1 CDB to save resources, easier patching",
        "example": "oradba pdb create --name HRDB --admin hrapps --password HRPass123"
    },
    
    "datapump": {
        "category": "advanced",
        "name": "Data Pump Export/Import",
        "description": "High-speed data migration tool",
        "commands": {
            "export": "oradba datapump export --schema APPUSER --file backup.dmp",
            "import": "oradba datapump import --file backup.dmp --remap NEWSCHEMA",
            "network-import": "oradba datapump network-import --source-db PRODDB --dest-db DEVDB"
        },
        "what_it_does": "Logical backup of schemas/tables to .dmp files. Faster than SQL*Loader. Can transform data during import",
        "when_to_use": "Migrate data between databases, refresh DEV from PROD, selective restores",
        "example": "oradba datapump export --schemas SALES,HR --parallel 4 --compress"
    },
}


def show_all_features():
    """Display all features organized by category"""
    console.print("\n[bold cyan]Oracle Database Features - Complete Reference[/bold cyan]\n")
    
    for cat_id, cat_info in FEATURE_CATEGORIES.items():
        # Category header
        console.print(f"\n{cat_info['icon']} [bold]{cat_info['name']}[/bold]")
        console.print(f"[dim]{cat_info['description']}[/dim]\n")
        
        # Features table
        table = Table(show_header=True, header_style="bold magenta", border_style="blue")
        table.add_column("Feature", style="cyan", width=25)
        table.add_column("Description", width=50)
        table.add_column("Quick Command", style="green", width=40)
        
        for feat_id, feat in FEATURES.items():
            if feat["category"] == cat_id:
                main_cmd = list(feat["commands"].values())[0]
                table.add_row(
                    feat["name"],
                    feat["description"],
                    main_cmd
                )
        
        console.print(table)
    
    console.print("\n[yellow]For detailed help on any feature:[/yellow]")
    console.print("  oradba help <feature-name>")
    console.print("\n[yellow]Examples:[/yellow]")
    console.print("  oradba help archivelog")
    console.print("  oradba help rman-backup")
    console.print("  oradba help dataguard\n")


def show_feature_detail(feature_name):
    """Show detailed help for specific feature"""
    # Find feature (case-insensitive, handle hyphens/underscores)
    feature_name_norm = feature_name.lower().replace('_', '-')
    
    feature = None
    feat_id = None
    for fid, feat in FEATURES.items():
        if fid == feature_name_norm or feat["name"].lower() == feature_name_norm:
            feature = feat
            feat_id = fid
            break
    
    if not feature:
        console.print(f"[red]✗ Feature '{feature_name}' not found[/red]")
        console.print("\n[yellow]Available features:[/yellow]")
        for fid, feat in FEATURES.items():
            console.print(f"  • {fid}")
        return False
    
    # Display detailed panel
    category = FEATURE_CATEGORIES[feature["category"]]
    
    console.print(f"\n{category['icon']} [bold cyan]{feature['name']}[/bold cyan]")
    console.print(f"[dim]Category: {category['name']}[/dim]\n")
    
    # Description
    console.print(Panel(feature["description"], title="Description", border_style="blue"))
    
    # What it does
    console.print(f"\n[bold]What it does:[/bold]")
    console.print(f"  {feature['what_it_does']}\n")
    
    # When to use
    console.print(f"[bold]When to use:[/bold]")
    console.print(f"  {feature['when_to_use']}\n")
    
    # Commands table
    console.print("[bold]Commands:[/bold]")
    cmd_table = Table(show_header=True, header_style="bold magenta", border_style="green")
    cmd_table.add_column("Action", style="yellow", width=20)
    cmd_table.add_column("Command", style="cyan", width=70)
    
    for action, cmd in feature["commands"].items():
        cmd_table.add_row(action.upper(), cmd)
    
    console.print(cmd_table)
    
    # Example
    console.print(f"\n[bold]Example:[/bold]")
    console.print(f"  {feature['example']}\n")
    
    return True


def show_quick_reference():
    """Show one-line quick reference of all commands"""
    console.print("\n[bold cyan]Quick Command Reference[/bold cyan]\n")
    
    for feat_id, feat in FEATURES.items():
        main_cmd = list(feat["commands"].values())[0]
        console.print(f"[cyan]{feat_id:25}[/cyan] {main_cmd}")
    
    console.print("\n[yellow]Tip:[/yellow] Use 'oradba help <feature>' for detailed documentation\n")


def show_workflow_guide():
    """Show recommended workflow for setting up production database"""
    console.print("\n[bold green]Production Database Setup Workflow[/bold green]\n")
    
    workflow = [
        ("1. System Preparation", "oradba precheck && oradba install system"),
        ("2. Install Oracle", "oradba install binaries --oracle-zip /path/to/oracle.zip"),
        ("3. Create Database", "oradba database create --sid PRODDB"),
        ("4. Enable Archive Mode", "oradba protection archivelog enable"),
        ("5. Configure FRA", "oradba protection fra enable --size 100G"),
        ("6. Multiplex Control Files", "oradba storage multiplex controlfile --copies 3"),
        ("7. Multiplex Redo Logs", "oradba storage multiplex redolog --members 2"),
        ("8. Enable Flashback", "oradba flashback database enable --retention 24h"),
        ("9. Configure RMAN", "oradba rman configure"),
        ("10. Create Tablespaces", "oradba storage tablespace create --name APP_DATA --size 10G"),
        ("11. Create Users", "oradba security user create --name APPUSER"),
        ("12. Setup Security Profile", "oradba security profile create --name PRODUCTION_POLICY"),
        ("13. Enable Audit", "oradba security audit enable"),
        ("14. First RMAN Backup", "oradba rman backup full"),
        ("15. Verify Everything", "oradba test --all"),
    ]
    
    table = Table(show_header=True, header_style="bold magenta", border_style="green")
    table.add_column("Step", style="yellow", width=5)
    table.add_column("Task", style="cyan", width=30)
    table.add_column("Command", style="green", width=60)
    
    for step, cmd in workflow:
        table.add_row(step.split('.')[0], step.split('.')[1].strip(), cmd)
    
    console.print(table)
    console.print("\n[bold]After setup, schedule:[/bold]")
    console.print("  • Daily full backup: oradba rman backup full")
    console.print("  • Hourly incremental: oradba rman backup incremental --level 1")
    console.print("  • Weekly AWR review: oradba tuning awr generate --last 7d")
    console.print("  • Monthly stats: oradba tuning stats gather --schema ALL\n")


def search_features(keyword):
    """Search features by keyword"""
    keyword_lower = keyword.lower()
    results = []
    
    for feat_id, feat in FEATURES.items():
        searchable = f"{feat_id} {feat['name']} {feat['description']} {feat['what_it_does']}".lower()
        if keyword_lower in searchable:
            results.append((feat_id, feat))
    
    if not results:
        console.print(f"[red]No features found matching '{keyword}'[/red]")
        return
    
    console.print(f"\n[bold cyan]Features matching '{keyword}':[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Feature ID", style="cyan", width=25)
    table.add_column("Name", style="yellow", width=30)
    table.add_column("Description", width=50)
    
    for feat_id, feat in results:
        table.add_row(feat_id, feat["name"], feat["description"])
    
    console.print(table)
    console.print(f"\n[yellow]Use 'oradba help <feature-id>' for details[/yellow]\n")
