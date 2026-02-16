"""
Cluster Manager - Gestion dynamique des nœuds Oracle
Permet d'ajouter/supprimer des nœuds, gérer SSH, configuration centralisée
"""

import os
import yaml
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from datetime import datetime
import paramiko

console = Console()


class ClusterManager:
    def __init__(self, config_dir=None):
        """
        Initialize cluster manager
        
        Args:
            config_dir: Directory to store cluster config (default: ~/.oracledba/)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / '.oracledba'
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'cluster.yaml'
        self.ssh_dir = self.config_dir / 'ssh_keys'
        self.ssh_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
    
    def _load_config(self):
        """Load cluster configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {
            'cluster_name': 'oracluster',
            'created_at': datetime.now().isoformat(),
            'nodes': {},
            'nfs_servers': {},
            'ssh_keys': {},
            'global_settings': {
                'oracle_base': '/u01/app/oracle',
                'oracle_home': '/u01/app/oracle/product/19.3.0/dbhome_1',
                'backup_location': '/backup',
                'fra_location': '/fra'
            }
        }
    
    def _save_config(self):
        """Save cluster configuration"""
        self.config['updated_at'] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        rprint(f"[green]✓[/green] Configuration saved: {self.config_file}")
    
    def add_node(self, name, ip, role='database', ssh_key=None, ssh_user='root', sid=None):
        """
        Add a node to the cluster
        
        Args:
            name: Node name (e.g., 'node1', 'nfs1')
            ip: IP address
            role: 'database', 'nfs', 'grid', 'standby'
            ssh_key: Path to SSH private key (will be copied to ~/.oracledba/ssh_keys/)
            ssh_user: SSH username (default: root)
            sid: Oracle SID for database nodes
        """
        console.print(f"\n[bold cyan]Adding node: {name}[/bold cyan]\n")
        
        # Validate node doesn't exist
        if name in self.config['nodes']:
            rprint(f"[yellow]⚠[/yellow] Node {name} already exists. Use update-node to modify.")
            return False
        
        # Copy SSH key if provided
        key_name = None
        if ssh_key:
            ssh_key_path = Path(ssh_key).expanduser()
            if not ssh_key_path.exists():
                rprint(f"[red]✗[/red] SSH key not found: {ssh_key}")
                return False
            
            # Copy key to cluster config directory
            key_name = f"{name}_rsa"
            dest_key = self.ssh_dir / key_name
            
            import shutil
            shutil.copy(ssh_key_path, dest_key)
            dest_key.chmod(0o600)
            
            rprint(f"[green]✓[/green] SSH key copied: {dest_key}")
            
            # Store key reference
            self.config['ssh_keys'][name] = str(dest_key)
        
        # Test SSH connection
        if ssh_key:
            rprint(f"[cyan]→[/cyan] Testing SSH connection to {ip}...")
            if not self._test_ssh(ip, ssh_user, str(dest_key)):
                rprint(f"[yellow]⚠[/yellow] SSH connection failed, but node will be added anyway")
        
        # Add node to config
        node_config = {
            'ip': ip,
            'role': role,
            'ssh_user': ssh_user,
            'ssh_key': key_name,
            'added_at': datetime.now().isoformat(),
            'status': 'registered'
        }
        
        if sid:
            node_config['sid'] = sid
        
        if role == 'database':
            node_config['oracle_base'] = self.config['global_settings']['oracle_base']
            node_config['oracle_home'] = self.config['global_settings']['oracle_home']
        
        self.config['nodes'][name] = node_config
        self._save_config()
        
        rprint(f"[green]✓[/green] Node {name} added successfully")
        self.show_node(name)
        
        return True
    
    def remove_node(self, name, force=False):
        """Remove a node from the cluster"""
        if name not in self.config['nodes']:
            rprint(f"[red]✗[/red] Node {name} not found")
            return False
        
        if not force:
            console.print(f"\n[yellow]⚠ Warning:[/yellow] This will remove {name} from cluster configuration")
            console.print("The actual machine and Oracle installation will NOT be affected.")
            console.print("Only the cluster metadata will be removed.\n")
            
            confirm = console.input(f"Remove {name}? (yes/no): ")
            if confirm.lower() != 'yes':
                rprint("[yellow]Cancelled[/yellow]")
                return False
        
        # Remove node
        del self.config['nodes'][name]
        
        # Remove SSH key if exists
        if name in self.config['ssh_keys']:
            key_path = Path(self.config['ssh_keys'][name])
            if key_path.exists():
                key_path.unlink()
            del self.config['ssh_keys'][name]
        
        self._save_config()
        rprint(f"[green]✓[/green] Node {name} removed from cluster")
        return True
    
    def list_nodes(self, role=None):
        """List all nodes in the cluster"""
        if not self.config['nodes']:
            rprint("[yellow]No nodes registered in cluster[/yellow]")
            return
        
        table = Table(title=f"Cluster: {self.config['cluster_name']}")
        table.add_column("Name", style="cyan")
        table.add_column("IP", style="green")
        table.add_column("Role", style="yellow")
        table.add_column("SID", style="magenta")
        table.add_column("SSH User", style="blue")
        table.add_column("Status", style="white")
        
        for name, node in self.config['nodes'].items():
            if role and node['role'] != role:
                continue
            
            table.add_row(
                name,
                node['ip'],
                node['role'],
                node.get('sid', '-'),
                node['ssh_user'],
                node['status']
            )
        
        console.print(table)
        console.print(f"\nTotal nodes: {len(self.config['nodes'])}")
        console.print(f"Config location: {self.config_file}")
    
    def show_node(self, name):
        """Show detailed information about a node"""
        if name not in self.config['nodes']:
            rprint(f"[red]✗[/red] Node {name} not found")
            return False
        
        node = self.config['nodes'][name]
        
        console.print(f"\n[bold cyan]Node: {name}[/bold cyan]")
        console.print(f"IP Address: {node['ip']}")
        console.print(f"Role: {node['role']}")
        console.print(f"SSH User: {node['ssh_user']}")
        console.print(f"SSH Key: {node.get('ssh_key', 'Not configured')}")
        console.print(f"Status: {node['status']}")
        
        if 'sid' in node:
            console.print(f"Oracle SID: {node['sid']}")
        if 'oracle_home' in node:
            console.print(f"Oracle Home: {node['oracle_home']}")
        
        console.print(f"Added: {node['added_at']}")
        
        return True
    
    def add_nfs_server(self, name, ip, export_paths, ssh_key=None):
        """
        Add NFS server to cluster
        
        Args:
            name: NFS server name
            ip: IP address
            export_paths: List of paths to export (e.g., ['/nfs/backup', '/nfs/fra'])
            ssh_key: SSH key path
        """
        console.print(f"\n[bold cyan]Adding NFS server: {name}[/bold cyan]\n")
        
        # Add as node first
        self.add_node(name, ip, role='nfs', ssh_key=ssh_key)
        
        # Add NFS-specific config
        self.config['nfs_servers'][name] = {
            'ip': ip,
            'export_paths': export_paths,
            'clients': []  # Will be populated when nodes mount
        }
        
        self._save_config()
        rprint(f"[green]✓[/green] NFS server {name} configured")
        return True
    
    def mount_nfs(self, node_name, nfs_server, remote_path, mount_point):
        """
        Configure NFS mount between node and NFS server
        
        Args:
            node_name: Database node name
            nfs_server: NFS server name
            remote_path: Path on NFS server (e.g., '/nfs/backup')
            mount_point: Mount point on node (e.g., '/backup')
        """
        if node_name not in self.config['nodes']:
            rprint(f"[red]✗[/red] Node {node_name} not found")
            return False
        
        if nfs_server not in self.config['nfs_servers']:
            rprint(f"[red]✗[/red] NFS server {nfs_server} not found")
            return False
        
        # Add mount configuration to node
        if 'nfs_mounts' not in self.config['nodes'][node_name]:
            self.config['nodes'][node_name]['nfs_mounts'] = []
        
        mount_config = {
            'nfs_server': nfs_server,
            'remote_path': remote_path,
            'mount_point': mount_point,
            'configured_at': datetime.now().isoformat()
        }
        
        self.config['nodes'][node_name]['nfs_mounts'].append(mount_config)
        
        # Add node to NFS clients
        node_ip = self.config['nodes'][node_name]['ip']
        if node_ip not in self.config['nfs_servers'][nfs_server]['clients']:
            self.config['nfs_servers'][nfs_server]['clients'].append(node_ip)
        
        self._save_config()
        rprint(f"[green]✓[/green] NFS mount configured: {node_name}:{mount_point} -> {nfs_server}:{remote_path}")
        return True
    
    def get_ssh_key(self, node_name):
        """Get SSH key path for a node"""
        if node_name not in self.config['nodes']:
            return None
        
        if node_name in self.config['ssh_keys']:
            return self.config['ssh_keys'][node_name]
        
        return None
    
    def _test_ssh(self, ip, user, key_path):
        """Test SSH connection to a node"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=ip,
                username=user,
                key_filename=key_path,
                timeout=10
            )
            client.close()
            return True
        except Exception as e:
            rprint(f"[red]SSH test failed:[/red] {str(e)}")
            return False
    
    def ssh_exec(self, node_name, command):
        """
        Execute command on a node via SSH
        
        Args:
            node_name: Node name in cluster
            command: Command to execute
        
        Returns:
            Tuple: (return_code, stdout, stderr)
        """
        if node_name not in self.config['nodes']:
            rprint(f"[red]✗[/red] Node {node_name} not found")
            return (1, "", "Node not found")
        
        node = self.config['nodes'][node_name]
        ssh_key = self.get_ssh_key(node_name)
        
        if not ssh_key:
            rprint(f"[red]✗[/red] No SSH key configured for {node_name}")
            return (1, "", "No SSH key")
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=node['ip'],
                username=node['ssh_user'],
                key_filename=ssh_key,
                timeout=30
            )
            
            stdin, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')
            
            client.close()
            
            return (exit_code, stdout_str, stderr_str)
        
        except Exception as e:
            rprint(f"[red]✗[/red] SSH execution failed: {str(e)}")
            return (1, "", str(e))
    
    def deploy_oracledba(self, node_name):
        """Deploy OracleDBA package on a node"""
        console.print(f"\n[bold cyan]Deploying OracleDBA on {node_name}[/bold cyan]\n")
        
        commands = """
        cd /root
        if [ -d oracledba ]; then
            rm -rf oracledba
        fi
        git clone https://github.com/ELMRABET-Abdelali/oracledba.git
        cd oracledba
        sudo bash install.sh
        """
        
        exit_code, stdout, stderr = self.ssh_exec(node_name, commands)
        
        if exit_code == 0:
            rprint(f"[green]✓[/green] OracleDBA deployed successfully on {node_name}")
            self.config['nodes'][node_name]['oracledba_installed'] = True
            self._save_config()
            return True
        else:
            rprint(f"[red]✗[/red] Deployment failed on {node_name}")
            console.print(stderr)
            return False
    
    def export_inventory(self, format='yaml'):
        """
        Export cluster inventory for Ansible/Terraform
        
        Args:
            format: 'yaml', 'ansible', 'terraform'
        """
        if format == 'ansible':
            # Generate Ansible inventory
            inventory = {
                'all': {
                    'children': {
                        'database_nodes': {
                            'hosts': {}
                        },
                        'nfs_servers': {
                            'hosts': {}
                        }
                    }
                }
            }
            
            for name, node in self.config['nodes'].items():
                if node['role'] == 'database':
                    inventory['all']['children']['database_nodes']['hosts'][name] = {
                        'ansible_host': node['ip'],
                        'ansible_user': node['ssh_user'],
                        'ansible_ssh_private_key_file': self.get_ssh_key(name),
                        'oracle_sid': node.get('sid', ''),
                        'oracle_home': node.get('oracle_home', '')
                    }
                elif node['role'] == 'nfs':
                    inventory['all']['children']['nfs_servers']['hosts'][name] = {
                        'ansible_host': node['ip'],
                        'ansible_user': node['ssh_user'],
                        'ansible_ssh_private_key_file': self.get_ssh_key(name)
                    }
            
            output_file = self.config_dir / 'ansible_inventory.yaml'
            with open(output_file, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False)
            
            rprint(f"[green]✓[/green] Ansible inventory exported: {output_file}")
            return str(output_file)
        
        else:
            # Default YAML export
            output_file = self.config_dir / 'cluster_export.yaml'
            with open(output_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            rprint(f"[green]✓[/green] Cluster configuration exported: {output_file}")
            return str(output_file)
