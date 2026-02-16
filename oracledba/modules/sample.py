#!/usr/bin/env python3
"""
Sample Database Generator
Creates a fully configured test database with sample data for learning and testing
"""

import os
import subprocess
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

console = Console()


class SampleDatabaseGenerator:
    """Generate and manage sample Oracle databases for testing"""
    
    def __init__(self, db_name="SAMPLEDB", oracle_home=None, oracle_base=None):
        self.db_name = db_name
        self.oracle_home = oracle_home or os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        self.oracle_base = oracle_base or os.environ.get('ORACLE_BASE', '/u01/app/oracle')
        
    def create_database(self):
        """Create complete sample database with DBCA"""
        console.print("\n[bold cyan]Creating sample database...[/bold cyan]")
        
        sql_script = f"""
-- Create sample database structure
CREATE TABLESPACE SAMPLE_DATA DATAFILE SIZE 500M AUTOEXTEND ON MAXSIZE 2G;
CREATE TABLESPACE SAMPLE_INDEX DATAFILE SIZE 200M AUTOEXTEND ON MAXSIZE 1G;

-- Create sample user
CREATE USER sample_user IDENTIFIED BY SamplePass123
DEFAULT TABLESPACE SAMPLE_DATA
TEMPORARY TABLESPACE TEMP
QUOTA UNLIMITED ON SAMPLE_DATA
QUOTA UNLIMITED ON SAMPLE_INDEX;

-- Grant privileges
GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE PROCEDURE TO sample_user;

-- Create sample tables
CREATE TABLE sample_user.customers (
    customer_id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100),
    phone VARCHAR2(20),
    created_date DATE DEFAULT SYSDATE
) TABLESPACE SAMPLE_DATA;

CREATE TABLE sample_user.orders (
    order_id NUMBER PRIMARY KEY,
    customer_id NUMBER REFERENCES sample_user.customers(customer_id),
    order_date DATE DEFAULT SYSDATE,
    total_amount NUMBER(10,2),
    status VARCHAR2(20)
) TABLESPACE SAMPLE_DATA;

CREATE TABLE sample_user.products (
    product_id NUMBER PRIMARY KEY,
    product_name VARCHAR2(100),
    price NUMBER(10,2),
    stock_quantity NUMBER
) TABLESPACE SAMPLE_DATA;

-- Create indexes
CREATE INDEX sample_user.idx_customer_email ON sample_user.customers(email) TABLESPACE SAMPLE_INDEX;
CREATE INDEX sample_user.idx_order_customer ON sample_user.orders(customer_id) TABLESPACE SAMPLE_INDEX;
CREATE INDEX sample_user.idx_order_date ON sample_user.orders(order_date) TABLESPACE SAMPLE_INDEX;

-- Insert sample data
BEGIN
    -- Insert customers
    FOR i IN 1..1000 LOOP
        INSERT INTO sample_user.customers VALUES (
            i,
            'Customer ' || i,
            'customer' || i || '@example.com',
            '+1-555-' || LPAD(i, 4, '0'),
            SYSDATE - DBMS_RANDOM.VALUE(1, 365)
        );
    END LOOP;
    
    -- Insert products
    FOR i IN 1..100 LOOP
        INSERT INTO sample_user.products VALUES (
            i,
            'Product ' || i,
            ROUND(DBMS_RANDOM.VALUE(10, 1000), 2),
            TRUNC(DBMS_RANDOM.VALUE(0, 500))
        );
    END LOOP;
    
    -- Insert orders
    FOR i IN 1..5000 LOOP
        INSERT INTO sample_user.orders VALUES (
            i,
            TRUNC(DBMS_RANDOM.VALUE(1, 1001)),
            SYSDATE - DBMS_RANDOM.VALUE(1, 180),
            ROUND(DBMS_RANDOM.VALUE(50, 5000), 2),
            CASE TRUNC(DBMS_RANDOM.VALUE(1, 5))
                WHEN 1 THEN 'PENDING'
                WHEN 2 THEN 'PROCESSING'
                WHEN 3 THEN 'SHIPPED'
                ELSE 'DELIVERED'
            END
        );
    END LOOP;
    
    COMMIT;
END;
/

-- Create sample procedures
CREATE OR REPLACE PROCEDURE sample_user.get_customer_orders(p_customer_id NUMBER) AS
    CURSOR order_cursor IS
        SELECT order_id, order_date, total_amount, status
        FROM orders
        WHERE customer_id = p_customer_id
        ORDER BY order_date DESC;
BEGIN
    FOR order_rec IN order_cursor LOOP
        DBMS_OUTPUT.PUT_LINE('Order: ' || order_rec.order_id || 
                           ' Date: ' || order_rec.order_date ||
                           ' Amount: ' || order_rec.total_amount);
    END LOOP;
END;
/

-- Gather statistics
EXEC DBMS_STATS.GATHER_SCHEMA_STATS('SAMPLE_USER');
"""
        
        return self._execute_sql(sql_script, "Sample database created successfully")
    
    def enable_archivelog(self):
        """Enable ARCHIVELOG mode for recovery features"""
        console.print("\n[bold cyan]Enabling ARCHIVELOG mode...[/bold cyan]")
        
        sql_script = """
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
SELECT log_mode FROM v$database;
"""
        return self._execute_sql(sql_script, "ARCHIVELOG mode enabled")
    
    def configure_fra(self, fra_size_gb=10):
        """Configure Fast Recovery Area"""
        console.print(f"\n[bold cyan]Configuring Fast Recovery Area ({fra_size_gb}GB)...[/bold cyan]")
        
        sql_script = f"""
ALTER SYSTEM SET db_recovery_file_dest_size={fra_size_gb}G SCOPE=BOTH;
ALTER SYSTEM SET db_recovery_file_dest='/u01/app/oracle/fra' SCOPE=BOTH;
"""
        return self._execute_sql(sql_script, "Fast Recovery Area configured")
    
    def multiplex_controlfiles(self):
        """Multiplex control files for redundancy"""
        console.print("\n[bold cyan]Multiplexing control files...[/bold cyan]")
        
        sql_script = f"""
-- Show current control files
SELECT name FROM v$controlfile;

-- Add multiplexed control file
ALTER SYSTEM SET control_files='/u01/app/oracle/oradata/{self.db_name}/control01.ctl',
                               '/u01/app/oracle/oradata/{self.db_name}/control02.ctl',
                               '/u01/app/oracle/oradata/{self.db_name}/control03.ctl' 
SCOPE=SPFILE;
"""
        
        console.print("[yellow]Note: Restart required. Run: oradba database restart[/yellow]")
        return self._execute_sql(sql_script, "Control files configured for multiplexing")
    
    def multiplex_redologs(self):
        """Multiplex redo log groups"""
        console.print("\n[bold cyan]Multiplexing redo logs...[/bold cyan]")
        
        sql_script = f"""
-- Add members to existing groups
ALTER DATABASE ADD LOGFILE MEMBER '/u01/app/oracle/oradata/{self.db_name}/redo01b.log' TO GROUP 1;
ALTER DATABASE ADD LOGFILE MEMBER '/u01/app/oracle/oradata/{self.db_name}/redo02b.log' TO GROUP 2;
ALTER DATABASE ADD LOGFILE MEMBER '/u01/app/oracle/oradata/{self.db_name}/redo03b.log' TO GROUP 3;

-- Verify
SELECT group#, member FROM v$logfile ORDER BY group#;
"""
        return self._execute_sql(sql_script, "Redo logs multiplexed")
    
    def enable_flashback(self):
        """Enable Flashback Database"""
        console.print("\n[bold cyan]Enabling Flashback Database...[/bold cyan]")
        
        sql_script = """
-- Configure retention (1 day)
ALTER SYSTEM SET db_flashback_retention_target=1440 SCOPE=BOTH;

-- Enable flashback
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE FLASHBACK ON;
ALTER DATABASE OPEN;

-- Verify
SELECT flashback_on FROM v$database;
"""
        return self._execute_sql(sql_script, "Flashback Database enabled")
    
    def configure_rman(self):
        """Configure RMAN with recommended settings"""
        console.print("\n[bold cyan]Configuring RMAN...[/bold cyan]")
        
        rman_script = """
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE DEVICE TYPE DISK BACKUP TYPE TO COMPRESSED BACKUPSET;
CONFIGURE BACKUP OPTIMIZATION ON;
SHOW ALL;
"""
        
        rman_file = f"/tmp/rman_config_{self.db_name}.rman"
        with open(rman_file, 'w') as f:
            f.write(rman_script)
        
        try:
            result = subprocess.run(
                ['rman', 'target', '/'],
                input=rman_script.encode(),
                capture_output=True,
                text=False
            )
            
            if result.returncode == 0:
                console.print("[green]✓ RMAN configured successfully[/green]")
                return True
            else:
                console.print(f"[red]✗ RMAN configuration failed[/red]")
                return False
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False
    
    def create_security_profile(self):
        """Create security profile with password policy"""
        console.print("\n[bold cyan]Creating security profile...[/bold cyan]")
        
        sql_script = """
-- Create security profile
CREATE PROFILE secure_profile LIMIT
    FAILED_LOGIN_ATTEMPTS 3
    PASSWORD_LIFE_TIME 90
    PASSWORD_REUSE_TIME 180
    PASSWORD_REUSE_MAX 5
    PASSWORD_LOCK_TIME 1/1440
    PASSWORD_GRACE_TIME 7;

-- Apply to sample user
ALTER USER sample_user PROFILE secure_profile;

-- Create admin user with higher privileges
CREATE USER db_admin IDENTIFIED BY AdminPass123
DEFAULT TABLESPACE SAMPLE_DATA
QUOTA UNLIMITED ON SAMPLE_DATA;

GRANT DBA TO db_admin;
ALTER USER db_admin PROFILE secure_profile;

-- Show profiles
SELECT profile, resource_name, limit FROM dba_profiles 
WHERE profile = 'SECURE_PROFILE'
ORDER BY resource_name;
"""
        return self._execute_sql(sql_script, "Security profile created")
    
    def show_status(self):
        """Show complete database status"""
        console.print("\n[bold cyan]Sample Database Status[/bold cyan]\n")
        
        sql_script = """
SET LINESIZE 200
SET PAGESIZE 100

PROMPT === Database Information ===
SELECT name, log_mode, open_mode, database_role FROM v$database;

PROMPT
PROMPT === Tablespaces ===
SELECT tablespace_name, status, contents, extent_management 
FROM dba_tablespaces 
ORDER BY tablespace_name;

PROMPT
PROMPT === Sample User Objects ===
SELECT object_type, COUNT(*) as count 
FROM dba_objects 
WHERE owner = 'SAMPLE_USER' 
GROUP BY object_type 
ORDER BY object_type;

PROMPT
PROMPT === Data Volume ===
SELECT 
    'Customers' as table_name, COUNT(*) as row_count 
FROM sample_user.customers
UNION ALL
SELECT 'Orders', COUNT(*) FROM sample_user.orders
UNION ALL
SELECT 'Products', COUNT(*) FROM sample_user.products;

PROMPT
PROMPT === Control Files ===
SELECT name FROM v$controlfile;

PROMPT
PROMPT === Redo Logs ===
SELECT group#, members, status FROM v$log;

PROMPT
PROMPT === FRA Configuration ===
SELECT name, value FROM v$parameter WHERE name LIKE '%recovery%';

PROMPT
PROMPT === RMAN Configuration ===
"""
        return self._execute_sql(sql_script, show_output=True)
    
    def cleanup(self):
        """Remove sample database and all associated objects"""
        console.print("\n[bold red]Cleaning up sample database...[/bold red]")
        
        sql_script = """
-- Drop sample user and all objects
DROP USER sample_user CASCADE;
DROP USER db_admin CASCADE;

-- Drop tablespaces
DROP TABLESPACE SAMPLE_DATA INCLUDING CONTENTS AND DATAFILES;
DROP TABLESPACE SAMPLE_INDEX INCLUDING CONTENTS AND DATAFILES;

-- Drop profile
DROP PROFILE secure_profile CASCADE;
"""
        return self._execute_sql(sql_script, "Sample database cleaned up")
    
    def _execute_sql(self, sql_script, success_msg=None, show_output=False):
        """Execute SQL script via sqlplus"""
        sql_file = f"/tmp/sample_db_{os.getpid()}.sql"
        
        try:
            # Write SQL to temp file
            with open(sql_file, 'w') as f:
                f.write("SET FEEDBACK ON\n")
                f.write("SET ECHO OFF\n")
                f.write("WHENEVER SQLERROR EXIT SQL.SQLCODE\n")
                f.write(sql_script)
                f.write("\nEXIT;\n")
            
            # Execute via sqlplus
            result = subprocess.run(
                ['sqlplus', '-S', '/', 'as', 'sysdba', f'@{sql_file}'],
                capture_output=True,
                text=True
            )
            
            if show_output:
                console.print(result.stdout)
            
            if result.returncode == 0:
                if success_msg:
                    console.print(f"[green]✓ {success_msg}[/green]")
                return True
            else:
                console.print(f"[red]✗ SQL execution failed[/red]")
                console.print(result.stderr)
                return False
                
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False
        finally:
            # Cleanup temp file
            if os.path.exists(sql_file):
                os.remove(sql_file)
    
    def run_full_setup(self):
        """Run complete sample database setup"""
        console.print("\n[bold green]Starting full sample database setup...[/bold green]\n")
        
        steps = [
            ("Creating database structure", self.create_database),
            ("Enabling ARCHIVELOG mode", self.enable_archivelog),
            ("Configuring Fast Recovery Area", lambda: self.configure_fra(10)),
            ("Multiplexing control files", self.multiplex_controlfiles),
            ("Multiplexing redo logs", self.multiplex_redologs),
            ("Enabling Flashback Database", self.enable_flashback),
            ("Configuring RMAN", self.configure_rman),
            ("Creating security profile", self.create_security_profile),
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for desc, func in steps:
                task = progress.add_task(desc, total=None)
                success = func()
                
                if not success:
                    console.print(f"\n[red]✗ Failed: {desc}[/red]")
                    return False
                
                progress.update(task, completed=True)
        
        console.print("\n[bold green]✓ Sample database fully configured![/bold green]")
        console.print("\n[cyan]Test connection:[/cyan]")
        console.print("  sqlplus sample_user/SamplePass123")
        console.print("\n[cyan]View status:[/cyan]")
        console.print("  oradba sample status")
        
        return True


def create_sample_db(db_name="SAMPLEDB"):
    """Create sample database with all features enabled"""
    generator = SampleDatabaseGenerator(db_name)
    return generator.run_full_setup()


def show_sample_status(db_name="SAMPLEDB"):
    """Show sample database status"""
    generator = SampleDatabaseGenerator(db_name)
    return generator.show_status()


def cleanup_sample_db(db_name="SAMPLEDB"):
    """Remove sample database"""
    generator = SampleDatabaseGenerator(db_name)
    return generator.cleanup()
