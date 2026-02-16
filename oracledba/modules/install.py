"""
Oracle Installation Manager
Handles Oracle 19c installation and system setup
"""

import os
import subprocess
import yaml
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()


class InstallManager:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
    
    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._default_config()
    
    def _default_config(self):
        """Return default configuration"""
        return {
            'oracle': {
                'oracle_base': '/u01/app/oracle',
                'oracle_home': '/u01/app/oracle/product/19.3.0/dbhome_1',
            },
            'database': {
                'db_name': 'GDCPROD',
                'sid': 'GDCPROD',
            }
        }
    
    def _run_script(self, script_name, as_user='root'):
        """Execute a bash script"""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            rprint(f"[red]Error:[/red] Script {script_name} not found")
            return False
        
        try:
            cmd = ['bash', str(script_path)]
            if as_user != 'root' and os.geteuid() == 0:
                cmd = ['su', '-', as_user, '-c', f'bash {script_path}']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                rprint(f"[green]✓[/green] {script_name} completed successfully")
                return True
            else:
                rprint(f"[red]✗[/red] {script_name} failed")
                rprint(result.stderr)
                return False
        except Exception as e:
            rprint(f"[red]Error executing {script_name}:[/red] {str(e)}")
            return False
    
    def install_full(self, skip_system=False, skip_binaries=False):
        """Complete Oracle installation"""
        console.print("\n[bold cyan]Starting Complete Oracle 19c Installation[/bold cyan]\n")
        
        steps = []
        if not skip_system:
            steps.append(("System Readiness", "tp01-system-readiness.sh", "root"))
        if not skip_binaries:
            steps.append(("Oracle Binaries", "tp02-installation-binaire.sh", "oracle"))
        steps.append(("Database Creation", "tp03-creation-instance.sh", "oracle"))
        steps.append(("Critical Files", "tp04-fichiers-critiques.sh", "oracle"))
        steps.append(("Storage Management", "tp05-gestion-stockage.sh", "oracle"))
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            for step_name, script, user in steps:
                task = progress.add_task(f"[cyan]{step_name}...", total=None)
                success = self._run_script(script, user)
                progress.remove_task(task)
                
                if not success:
                    rprint(f"\n[red]Installation failed at step: {step_name}[/red]")
                    return False
        
        console.print("\n[bold green]✓ Oracle 19c installation completed successfully![/bold green]")
        return True
    
    def install_system(self):
        """Install system prerequisites"""
        console.print("\n[bold cyan]Installing System Prerequisites[/bold cyan]\n")
        return self._run_script("tp01-system-readiness.sh", "root")
    
    def install_binaries(self):
        """Install Oracle binaries"""
        console.print("\n[bold cyan]Installing Oracle Binaries[/bold cyan]\n")
        return self._run_script("tp02-installation-binaire.sh", "oracle")
    
    def create_database(self, db_name=None):
        """Create Oracle database"""
        if db_name:
            os.environ['ORACLE_SID'] = db_name
        
        console.print("\n[bold cyan]Creating Oracle Database[/bold cyan]\n")
        return self._run_script("tp03-creation-instance.sh", "oracle")
    
    def vm_init(self, role, node_number=None):
        """Initialize VM for Oracle"""
        console.print(f"\n[bold cyan]Initializing VM as {role}[/bold cyan]\n")
        
        if role == 'database':
            return self.install_system()
        elif role == 'rac-node':
            rprint(f"[cyan]Setting up RAC node {node_number}[/cyan]")
            # RAC-specific setup
            return self._run_script("tp15-asm-rac-concepts.sh", "root")
        elif role == 'dataguard-standby':
            rprint("[cyan]Setting up Data Guard standby[/cyan]")
            return self._run_script("tp09-dataguard.sh", "oracle")
        
        return False
