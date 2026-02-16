#!/usr/bin/env python3
"""
OracleDBA CLI - Main Command Line Interface
Complete Oracle Database Administration Tool
"""

import os
import sys
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

console = Console()

# Import modules
from .modules import install
from .modules import rman
from .modules import dataguard
from .modules import tuning
from .modules import asm
from .modules import rac
from .modules import pdb
from .modules import flashback
from .modules import security
from .modules import nfs
from .modules import database
from .utils import logger

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def main(ctx, version):
    """
    🗄️  OracleDBA - Complete Oracle Database Administration Tool
    
    Installation, backup, tuning, ASM, RAC, and more for Oracle 19c
    """
    if version:
        from . import __version__
        rprint(f"[bold green]OracleDBA[/bold green] version [cyan]{__version__}[/cyan]")
        return
    
    if ctx.invoked_subcommand is None:
        show_banner()
        rprint("\n[yellow]Use[/yellow] [cyan]oradba --help[/cyan] [yellow]for available commands[/yellow]\n")


def show_banner():
    """Display banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     🗄️   OracleDBA - Database Administration Tool    ║
    ║                                                       ║
    ║     Complete package for Oracle 19c on Rocky Linux   ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))


# ============================================================================
# INSTALLATION COMMANDS
# ============================================================================

@main.group()
def install():
    """📦 Install and configure Oracle Database"""
    pass


@install.command('full')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--skip-system', is_flag=True, help='Skip system setup')
@click.option('--skip-binaries', is_flag=True, help='Skip binary installation')
def install_full(config, skip_system, skip_binaries):
    """Complete Oracle 19c installation"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    mgr.install_full(skip_system, skip_binaries)


@install.command('system')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
def install_system(config):
    """Prepare system (users, groups, kernel params)"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    mgr.install_system()


@install.command('binaries')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
def install_binaries(config):
    """Install Oracle binaries"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    mgr.install_binaries()


@install.command('database')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--name', help='Database name')
def install_database(config, name):
    """Create Oracle database"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    mgr.create_database(name)


# ============================================================================
# PRE-INSTALLATION CHECK
# ============================================================================

@main.command('precheck')
@click.option('--fix', is_flag=True, help='Generate fix script')
def precheck(fix):
    """🔍 Check system requirements before installation"""
    from .modules.precheck import PreInstallChecker
    checker = PreInstallChecker()
    result = checker.check_all()
    
    if fix or not result:
        checker.generate_fix_script()
        console.print("\n[cyan]Run:[/cyan] sudo bash fix-precheck-issues.sh")


# ============================================================================
# TESTING COMMANDS
# ============================================================================

@main.command('test')
@click.option('--oracle-home', help='ORACLE_HOME path')
@click.option('--oracle-sid', help='ORACLE_SID name')
@click.option('--report', is_flag=True, help='Generate detailed report')
def test(oracle_home, oracle_sid, report):
    """🧪 Test Oracle installation"""
    from .modules.testing import OracleTestSuite
    tester = OracleTestSuite(oracle_home, oracle_sid)
    result = tester.run_all_tests()
    
    if report:
        tester.generate_test_report()


# ============================================================================
# DOWNLOAD ORACLE SOFTWARE
# ============================================================================

@main.group()
def download():
    """📥 Download Oracle software"""
    pass


@download.command('database')
@click.option('--url', help='Custom download URL')
@click.option('--dir', default='/opt/oracle/install', help='Download directory')
def download_database(url, dir):
    """Download Oracle 19c Database software"""
    from .modules.downloader import OracleDownloader
    downloader = OracleDownloader(dir)
    downloader.download_oracle_19c('database', url)


@download.command('grid')
@click.option('--url', help='Custom download URL')
@click.option('--dir', default='/opt/oracle/install', help='Download directory')
def download_grid(url, dir):
    """Download Oracle Grid Infrastructure software"""
    from .modules.downloader import OracleDownloader
    downloader = OracleDownloader(dir)
    downloader.download_oracle_19c('grid', url)


@download.command('extract')
@click.argument('zip-file')
@click.option('--to', 'extract_to', help='Extract to directory (ORACLE_HOME)')
def download_extract(zip_file, extract_to):
    """Extract Oracle ZIP file"""
    from .modules.downloader import OracleDownloader
    downloader = OracleDownloader()
    downloader.extract_oracle_zip(zip_file, extract_to)


# ============================================================================
# RESPONSE FILE GENERATION
# ============================================================================

@main.group()
def genrsp():
    """📝 Generate Oracle response files"""
    pass


@genrsp.command('all')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--output-dir', default='/tmp', help='Output directory')
def genrsp_all(config, output_dir):
    """Generate all response files (DB, DBCA, NETCA)"""
    from .modules.response_files import generate_all_response_files
    files = generate_all_response_files(config, output_dir)
    
    console.print("\n[green]✓[/green] Response files generated:")
    for name, path in files.items():
        console.print(f"  • {name}: {path}")


@genrsp.command('db-install')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--output', default='/tmp/db_install.rsp', help='Output file')
def genrsp_db(config, output):
    """Generate DB installation response file"""
    from .modules.response_files import generate_response_file
    import yaml
    
    cfg = {}
    if config:
        with open(config) as f:
            cfg = yaml.safe_load(f).get('oracle', {})
    
    _, actual_file = generate_response_file('DB_INSTALL', cfg, output)
    console.print(f"[green]✓[/green] Generated: {actual_file}")


@genrsp.command('dbca')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--output', default='/tmp/dbca.rsp', help='Output file')
def genrsp_dbca(config, output):
    """Generate DBCA response file"""
    from .modules.response_files import generate_response_file
    import yaml
    
    cfg = {}
    if config:
        with open(config) as f:
            cfg = yaml.safe_load(f).get('database', {})
    
    _, actual_file = generate_response_file('DBCA', cfg, output)
    console.print(f"[green]✓[/green] Generated: {actual_file}")


# ============================================================================
# RMAN COMMANDS
# ============================================================================

@main.group()
def rman():
    """💾 RMAN Backup and Recovery"""
    pass


@rman.command('setup')
@click.option('--retention', default=7, help='Retention policy in days')
@click.option('--compression', is_flag=True, default=True, help='Enable compression')
def rman_setup(retention, compression):
    """Configure RMAN"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.setup(retention, compression)


@rman.command('backup')
@click.option('--type', type=click.Choice(['full', 'incremental', 'archive']), default='full')
@click.option('--tag', help='Backup tag')
def rman_backup(type, tag):
    """Perform RMAN backup"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.backup(type, tag)


@rman.command('restore')
@click.option('--point-in-time', help='Point in time (YYYY-MM-DD HH:MI:SS)')
def rman_restore(point_in_time):
    """Restore database with RMAN"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.restore(point_in_time)


@rman.command('list')
@click.option('--type', type=click.Choice(['backup', 'archivelog', 'all']), default='backup')
def rman_list(type):
    """List RMAN backups"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.list_backups(type)


# ============================================================================
# DATA GUARD COMMANDS
# ============================================================================

@main.group()
def dataguard():
    """🔄 Data Guard Management"""
    pass


@dataguard.command('setup')
@click.option('--primary-host', required=True, help='Primary database host')
@click.option('--standby-host', required=True, help='Standby database host')
@click.option('--db-name', required=True, help='Database name')
def dataguard_setup(primary_host, standby_host, db_name):
    """Configure Data Guard"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.setup(primary_host, standby_host, db_name)


@dataguard.command('status')
def dataguard_status():
    """Check Data Guard status"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.status()


@dataguard.command('switchover')
def dataguard_switchover():
    """Perform switchover"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.switchover()


@dataguard.command('failover')
def dataguard_failover():
    """Perform failover"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.failover()


# ============================================================================
# TUNING COMMANDS
# ============================================================================

@main.group()
def tuning():
    """⚡ Performance Tuning"""
    pass


@tuning.command('analyze')
@click.option('--deep', is_flag=True, help='Deep analysis')
def tuning_analyze(deep):
    """Analyze database performance"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.analyze(deep)


@tuning.command('awr')
@click.option('--begin-snap', type=int, help='Begin snapshot ID')
@click.option('--end-snap', type=int, help='End snapshot ID')
def tuning_awr(begin_snap, end_snap):
    """Generate AWR report"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.generate_awr(begin_snap, end_snap)


@tuning.command('addm')
def tuning_addm():
    """Generate ADDM report"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.generate_addm()


@tuning.command('sql-trace')
@click.option('--session-id', type=int, help='Session ID to trace')
def tuning_sql_trace(session_id):
    """Enable SQL trace"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.sql_trace(session_id)


# ============================================================================
# ASM COMMANDS
# ============================================================================

@main.group()
def asm():
    """💿 Automatic Storage Management"""
    pass


@asm.command('setup')
@click.option('--disks', multiple=True, help='Disk devices')
def asm_setup(disks):
    """Configure ASM"""
    from .modules.asm import ASMManager
    mgr = ASMManager()
    mgr.setup(list(disks))


@asm.command('create-diskgroup')
@click.option('--name', required=True, help='Diskgroup name')
@click.option('--redundancy', type=click.Choice(['EXTERNAL', 'NORMAL', 'HIGH']), default='NORMAL')
@click.option('--disks', multiple=True, required=True, help='Disk paths')
def asm_create_diskgroup(name, redundancy, disks):
    """Create ASM diskgroup"""
    from .modules.asm import ASMManager
    mgr = ASMManager()
    mgr.create_diskgroup(name, redundancy, list(disks))


@asm.command('status')
def asm_status():
    """Check ASM status"""
    from .modules.asm import ASMManager
    mgr = ASMManager()
    mgr.status()


# ============================================================================
# RAC COMMANDS
# ============================================================================

@main.group()
def rac():
    """🔗 Real Application Clusters"""
    pass


@rac.command('setup')
@click.option('--nodes', multiple=True, required=True, help='Node hostnames')
@click.option('--vip', multiple=True, required=True, help='Virtual IPs')
def rac_setup(nodes, vip):
    """Configure RAC"""
    from .modules.rac import RACManager
    mgr = RACManager()
    mgr.setup(list(nodes), list(vip))


@rac.command('add-node')
@click.option('--hostname', required=True, help='New node hostname')
@click.option('--vip', required=True, help='Virtual IP')
def rac_add_node(hostname, vip):
    """Add RAC node"""
    from .modules.rac import RACManager
    mgr = RACManager()
    mgr.add_node(hostname, vip)


@rac.command('status')
def rac_status():
    """Check RAC cluster status"""
    from .modules.rac import RACManager
    mgr = RACManager()
    mgr.status()


# ============================================================================
# MULTITENANT (PDB) COMMANDS
# ============================================================================

@main.group()
def pdb():
    """🏢 Multitenant - PDB Management"""
    pass


@pdb.command('create')
@click.argument('name')
@click.option('--admin-user', default='pdbadmin', help='PDB admin user')
@click.option('--admin-password', prompt=True, hide_input=True, help='Admin password')
def pdb_create(name, admin_user, admin_password):
    """Create new PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.create(name, admin_user, admin_password)


@pdb.command('clone')
@click.argument('source')
@click.argument('destination')
def pdb_clone(source, destination):
    """Clone PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.clone(source, destination)


@pdb.command('list')
def pdb_list():
    """List all PDBs"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.list_pdbs()


@pdb.command('open')
@click.argument('name')
def pdb_open(name):
    """Open PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.open(name)


@pdb.command('close')
@click.argument('name')
def pdb_close(name):
    """Close PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.close(name)


@pdb.command('drop')
@click.argument('name')
@click.option('--including-datafiles', is_flag=True, help='Drop including datafiles')
def pdb_drop(name, including_datafiles):
    """Drop PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.drop(name, including_datafiles)


# ============================================================================
# FLASHBACK COMMANDS
# ============================================================================

@main.group()
def flashback():
    """📊 Flashback Technology"""
    pass


@flashback.command('enable')
@click.option('--retention', default=2880, help='Retention in minutes (default 2 days)')
def flashback_enable(retention):
    """Enable Flashback Database"""
    from .modules.flashback import FlashbackManager
    mgr = FlashbackManager()
    mgr.enable(retention)


@flashback.command('disable')
def flashback_disable():
    """Disable Flashback Database"""
    from .modules.flashback import FlashbackManager
    mgr = FlashbackManager()
    mgr.disable()


@flashback.command('restore')
@click.option('--point-in-time', help='Point in time')
@click.option('--scn', type=int, help='SCN number')
def flashback_restore(point_in_time, scn):
    """Restore database with Flashback"""
    from .modules.flashback import FlashbackManager
    mgr = FlashbackManager()
    mgr.restore(point_in_time, scn)


# ============================================================================
# SECURITY COMMANDS
# ============================================================================

@main.group()
def security():
    """🔐 Security Management"""
    pass


@security.command('audit')
@click.option('--enable', is_flag=True, help='Enable auditing')
def security_audit(enable):
    """Configure auditing"""
    from .modules.security import SecurityManager
    mgr = SecurityManager()
    mgr.configure_audit(enable)


@security.command('encryption')
@click.option('--enable', is_flag=True, help='Enable TDE')
def security_encryption(enable):
    """Configure Transparent Data Encryption"""
    from .modules.security import SecurityManager
    mgr = SecurityManager()
    mgr.configure_tde(enable)


@security.command('users')
@click.option('--create', help='Create user')
@click.option('--drop', help='Drop user')
@click.option('--list', 'list_users', is_flag=True, help='List users')
def security_users(create, drop, list_users):
    """Manage database users"""
    from .modules.security import SecurityManager
    mgr = SecurityManager()
    if create:
        mgr.create_user(create)
    elif drop:
        mgr.drop_user(drop)
    elif list_users:
        mgr.list_users()


# ============================================================================
# NFS COMMANDS
# ============================================================================

@main.group()
def nfs():
    """🌐 NFS Server Management"""
    pass


@nfs.command('setup-server')
@click.option('--export', required=True, help='Export path')
@click.option('--clients', multiple=True, help='Allowed client IPs/networks')
def nfs_setup_server(export, clients):
    """Setup NFS server"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.setup_server(export, list(clients))


@nfs.command('setup-client')
@click.option('--server', required=True, help='NFS server IP')
@click.option('--remote-path', required=True, help='Remote export path')
@click.option('--mount-point', required=True, help='Local mount point')
def nfs_setup_client(server, remote_path, mount_point):
    """Setup NFS client"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.setup_client(server, remote_path, mount_point)


@nfs.command('mount')
@click.option('--server', required=True, help='NFS server')
@click.option('--path', required=True, help='Remote path')
@click.option('--mount-point', required=True, help='Mount point')
def nfs_mount(server, path, mount_point):
    """Mount NFS share"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.mount(server, path, mount_point)


@nfs.command('share')
@click.argument('directory')
@click.option('--clients', multiple=True, help='Allowed clients')
def nfs_share(directory, clients):
    """Share directory via NFS"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.share(directory, list(clients))


# ============================================================================
# DATABASE MANAGEMENT COMMANDS
# ============================================================================

@main.command()
def status():
    """📊 Show database status"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.show_status()


@main.command()
def start():
    """▶️  Start database"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.start()


@main.command()
def stop():
    """⏹️  Stop database"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.stop()


@main.command()
def restart():
    """🔄 Restart database"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.restart()


@main.command()
@click.option('--sysdba', is_flag=True, help='Connect as SYSDBA')
@click.option('--pdb', help='Connect to specific PDB')
def sqlplus(sysdba, pdb):
    """🔌 Connect to SQL*Plus"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.sqlplus(sysdba, pdb)


@main.command()
@click.argument('script', type=click.Path(exists=True))
@click.option('--as-sysdba', is_flag=True, help='Execute as SYSDBA')
def exec(script, as_sysdba):
    """⚙️  Execute SQL or Shell script"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.exec_script(script, as_sysdba)


# ============================================================================
# MONITORING COMMANDS
# ============================================================================

@main.group()
def logs():
    """📝 View logs"""
    pass


@logs.command('alert')
@click.option('--tail', default=50, help='Number of lines to show')
def logs_alert(tail):
    """View alert log"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.view_alert_log(tail)


@logs.command('listener')
@click.option('--tail', default=50, help='Number of lines to show')
def logs_listener(tail):
    """View listener log"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.view_listener_log(tail)


@main.group()
def monitor():
    """📈 Monitor database"""
    pass


@monitor.command('tablespaces')
def monitor_tablespaces():
    """Monitor tablespace usage"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.monitor_tablespaces()


@monitor.command('sessions')
@click.option('--active-only', is_flag=True, help='Show only active sessions')
def monitor_sessions(active_only):
    """Monitor database sessions"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.monitor_sessions(active_only)


# ============================================================================
# VM INITIALIZATION
# ============================================================================

@main.command('vm-init')
@click.option('--role', type=click.Choice(['database', 'rac-node', 'dataguard-standby']), required=True)
@click.option('--node-number', type=int, help='Node number for RAC')
def vm_init(role, node_number):
    """🖥️  Initialize new VM for Oracle"""
    from .modules.install import InstallManager
    mgr = InstallManager()
    mgr.vm_init(role, node_number)


# ============================================================================
# CLUSTER MANAGEMENT
# ============================================================================

@main.group()
def cluster():
    """🖧  Manage multi-node Oracle cluster"""
    pass


@cluster.command('add-node')
@click.option('--name', required=True, help='Node name (e.g., node1, node2)')
@click.option('--ip', required=True, help='IP address')
@click.option('--role', type=click.Choice(['database', 'nfs', 'grid', 'standby']), default='database', help='Node role')
@click.option('--ssh-key', help='Path to SSH private key')
@click.option('--ssh-user', default='root', help='SSH username')
@click.option('--sid', help='Oracle SID for database nodes')
def cluster_add_node(name, ip, role, ssh_key, ssh_user, sid):
    """Add a node to the cluster"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    mgr.add_node(name, ip, role, ssh_key, ssh_user, sid)


@cluster.command('remove-node')
@click.argument('name')
@click.option('--force', is_flag=True, help='Skip confirmation')
def cluster_remove_node(name, force):
    """Remove a node from the cluster"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    mgr.remove_node(name, force)


@cluster.command('list')
@click.option('--role', type=click.Choice(['database', 'nfs', 'grid', 'standby']), help='Filter by role')
def cluster_list(role):
    """List all nodes in the cluster"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    mgr.list_nodes(role)


@cluster.command('show')
@click.argument('name')
def cluster_show(name):
    """Show detailed information about a node"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    mgr.show_node(name)


@cluster.command('add-nfs')
@click.option('--name', required=True, help='NFS server name')
@click.option('--ip', required=True, help='IP address')
@click.option('--exports', required=True, help='Export paths (comma-separated, e.g., /nfs/backup,/nfs/fra)')
@click.option('--ssh-key', help='Path to SSH private key')
def cluster_add_nfs(name, ip, exports, ssh_key):
    """Add NFS server to the cluster"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    export_paths = [p.strip() for p in exports.split(',')]
    mgr.add_nfs_server(name, ip, export_paths, ssh_key)


@cluster.command('mount-nfs')
@click.option('--node', required=True, help='Database node name')
@click.option('--nfs-server', required=True, help='NFS server name')
@click.option('--remote-path', required=True, help='Remote path on NFS (e.g., /nfs/backup)')
@click.option('--mount-point', required=True, help='Local mount point (e.g., /backup)')
def cluster_mount_nfs(node, nfs_server, remote_path, mount_point):
    """Configure NFS mount between node and NFS server"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    mgr.mount_nfs(node, nfs_server, remote_path, mount_point)


@cluster.command('deploy')
@click.argument('node_name')
def cluster_deploy(node_name):
    """Deploy OracleDBA package on a node"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    mgr.deploy_oracledba(node_name)


@cluster.command('ssh')
@click.argument('node_name')
@click.argument('command', nargs=-1, required=True)
def cluster_ssh(node_name, command):
    """Execute command on a node via SSH"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    cmd = ' '.join(command)
    exit_code, stdout, stderr = mgr.ssh_exec(node_name, cmd)
    
    if stdout:
        console.print(stdout)
    if stderr:
        console.print(f"[red]{stderr}[/red]", style="bold")
    
    sys.exit(exit_code)


@cluster.command('export')
@click.option('--format', type=click.Choice(['yaml', 'ansible', 'terraform']), default='yaml', help='Export format')
def cluster_export(format):
    """Export cluster inventory"""
    from .modules.cluster import ClusterManager
    mgr = ClusterManager()
    output_file = mgr.export_inventory(format)
    console.print(f"\n[green]✓[/green] Inventory exported: {output_file}")


# ============================================================================
# SAMPLE DATABASE COMMANDS
# ============================================================================

@main.group()
def sample():
    """🧪 Sample database for testing and learning"""
    pass


@sample.command('create')
@click.option('--name', default='SAMPLEDB', help='Sample database name')
def sample_create(name):
    """Create fully configured sample database with test data"""
    from .modules.sample import SampleDatabaseGenerator
    console.print("[bold cyan]Creating sample database...[/bold cyan]")
    console.print("[dim]This includes: tables, data, indexes, security, backups, flashback[/dim]\n")
    
    generator = SampleDatabaseGenerator(name)
    success = generator.run_full_setup()
    
    if success:
        console.print("\n[bold green]✓ Sample database ready![/bold green]")
        console.print("\n[cyan]Try these commands:[/cyan]")
        console.print("  oradba sample status       # View configuration")
        console.print("  oradba sample test         # Test all features")
        console.print("  oradba sample connect      # Get connection string")
    else:
        console.print("\n[bold red]✗ Sample database creation failed[/bold red]")
        sys.exit(1)


@sample.command('status')
@click.option('--name', default='SAMPLEDB', help='Sample database name')
def sample_status(name):
    """Show sample database configuration and statistics"""
    from .modules.sample import SampleDatabaseGenerator
    generator = SampleDatabaseGenerator(name)
    generator.show_status()


@sample.command('test')
@click.option('--name', default='SAMPLEDB', help='Sample database name')
@click.option('--feature', help='Test specific feature (archivelog, rman, flashback, security)')
def sample_test(name, feature):
    """Test sample database features"""
    console.print(f"\n[bold cyan]Testing sample database: {name}[/bold cyan]\n")
    
    tests = {
        'connection': {
            'name': 'Database Connection',
            'sql': "SELECT 'Connected to ' || instance_name FROM v$instance;"
        },
        'archivelog': {
            'name': 'Archive Log Mode',
            'sql': "SELECT log_mode FROM v$database;"
        },
        'fra': {
            'name': 'Fast Recovery Area',
            'sql': "SELECT name, value FROM v$parameter WHERE name LIKE '%recovery_file_dest%';"
        },
        'controlfiles': {
            'name': 'Control File Multiplexing',
            'sql': "SELECT COUNT(*) as multiplexed_copies FROM v$controlfile;"
        },
        'redologs': {
            'name': 'Redo Log Multiplexing',
            'sql': "SELECT group#, COUNT(*) as members FROM v$logfile GROUP BY group#;"
        },
        'flashback': {
            'name': 'Flashback Database',
            'sql': "SELECT flashback_on FROM v$database;"
        },
        'sample_data': {
            'name': 'Sample Data',
            'sql': "SELECT 'Customers: ' || COUNT(*) FROM sample_user.customers UNION ALL SELECT 'Orders: ' || COUNT(*) FROM sample_user.orders;"
        },
        'security': {
            'name': 'Security Profile',
            'sql': "SELECT username, profile FROM dba_users WHERE username = 'SAMPLE_USER';"
        }
    }
    
    if feature:
        if feature not in tests:
            console.print(f"[red]Unknown feature: {feature}[/red]")
            console.print("[yellow]Available:[/yellow] " + ", ".join(tests.keys()))
            sys.exit(1)
        tests_to_run = {feature: tests[feature]}
    else:
        tests_to_run = tests
    
    all_passed = True
    for test_id, test_info in tests_to_run.items():
        console.print(f"[cyan]Testing:[/cyan] {test_info['name']}")
        
        # Execute test SQL
        import subprocess
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(f"SET FEEDBACK OFF\n")
            f.write(f"SET HEADING OFF\n")
            f.write(f"{test_info['sql']}\n")
            f.write("EXIT;\n")
            sql_file = f.name
        
        try:
            result = subprocess.run(
                ['sqlplus', '-S', '/', 'as', 'sysdba', f'@{sql_file}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                console.print(f"  [green]✓ PASS[/green] - {result.stdout.strip()}")
            else:
                console.print(f"  [red]✗ FAIL[/red]")
                all_passed = False
        except Exception as e:
            console.print(f"  [red]✗ ERROR:[/red] {e}")
            all_passed = False
        finally:
            os.unlink(sql_file)
    
    if all_passed:
        console.print("\n[bold green]✓ All tests passed![/bold green]")
    else:
        console.print("\n[bold red]✗ Some tests failed[/bold red]")
        sys.exit(1)


@sample.command('connect')
@click.option('--name', default='SAMPLEDB', help='Sample database name')
@click.option('--user', default='sample_user', help='User name')
def sample_connect(name, user):
    """Show connection string for sample database"""
    console.print(f"\n[bold cyan]Sample Database Connection Info[/bold cyan]\n")
    
    console.print("[yellow]SQL*Plus:[/yellow]")
    console.print(f"  sqlplus {user}/SamplePass123@{name}")
    
    console.print("\n[yellow]JDBC:[/yellow]")
    console.print(f"  jdbc:oracle:thin:@localhost:1521:{name}")
    
    console.print("\n[yellow]Python (cx_Oracle):[/yellow]")
    console.print(f"  cx_Oracle.connect('{user}', 'SamplePass123', 'localhost:1521/{name}')")
    
    console.print("\n[yellow]TNS:[/yellow]")
    console.print(f"  {name} = (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME={name})))\n")


@sample.command('remove')
@click.option('--name', default='SAMPLEDB', help='Sample database name')
@click.option('--force', is_flag=True, help='Skip confirmation')
def sample_remove(name, force):
    """Remove sample database and all data"""
    if not force:
        console.print(f"\n[bold red]WARNING:[/bold red] This will DELETE sample database '{name}' and ALL DATA")
        confirm = input("Type 'yes' to confirm: ")
        if confirm != 'yes':
            console.print("[yellow]Cancelled[/yellow]")
            return
    
    from .modules.sample import SampleDatabaseGenerator
    generator = SampleDatabaseGenerator(name)
    success = generator.cleanup()
    
    if success:
        console.print(f"\n[green]✓ Sample database '{name}' removed[/green]")
    else:
        console.print(f"\n[red]✗ Failed to remove sample database[/red]")
        sys.exit(1)


# ============================================================================
# ENHANCED HELP SYSTEM
# ============================================================================

@main.group()
def help():
    """📚 Comprehensive help and documentation"""
    pass


@help.command('features')
def help_features():
    """List all Oracle features with descriptions"""
    from .modules.help_system import show_all_features
    show_all_features()


@help.command('feature')
@click.argument('feature_name')
def help_feature(feature_name):
    """Show detailed help for specific feature"""
    from .modules.help_system import show_feature_detail
    show_feature_detail(feature_name)


@help.command('workflow')
def help_workflow():
    """Show recommended production setup workflow"""
    from .modules.help_system import show_workflow_guide
    show_workflow_guide()


@help.command('search')
@click.argument('keyword')
def help_search(keyword):
    """Search features by keyword"""
    from .modules.help_system import search_features
    search_features(keyword)


@help.command('quick')
def help_quick():
    """Quick command reference (one-liners)"""
    from .modules.help_system import show_quick_reference
    show_quick_reference()


if __name__ == '__main__':
    main()
