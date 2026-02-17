#!/usr/bin/env python3
"""
System Detector Module
Detects what's installed, what's running, and what can be activated
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


class SystemDetector:
    """Detects Oracle components and their status"""
    
    def __init__(self):
        self.oracle_home = os.environ.get('ORACLE_HOME', '')
        self.oracle_sid = os.environ.get('ORACLE_SID', '')
    
    def detect_all(self) -> Dict:
        """Detect all system components and their status"""
        return {
            'oracle': self.detect_oracle(),
            'database': self.detect_database(),
            'listener': self.detect_listener(),
            'grid': self.detect_grid_infrastructure(),
            'asm': self.detect_asm(),
            'cluster': self.detect_cluster(),
            'features': self.detect_features()
        }
    
    def detect_oracle(self) -> Dict:
        """Detect Oracle installation"""
        result = {
            'installed': False,
            'version': None,
            'oracle_home': self.oracle_home,
            'binaries': {
                'sqlplus': False,
                'rman': False,
                'lsnrctl': False,
                'dbca': False
            }
        }
        
        # Check if ORACLE_HOME is set and exists
        if self.oracle_home and Path(self.oracle_home).exists():
            result['installed'] = True
            
            # Check for binaries
            bin_dir = Path(self.oracle_home) / 'bin'
            if bin_dir.exists():
                result['binaries']['sqlplus'] = (bin_dir / 'sqlplus').exists()
                result['binaries']['rman'] = (bin_dir / 'rman').exists()
                result['binaries']['lsnrctl'] = (bin_dir / 'lsnrctl').exists()
                result['binaries']['dbca'] = (bin_dir / 'dbca').exists()
            
            # Try to get version
            try:
                if result['binaries']['sqlplus']:
                    cmd = f"{bin_dir / 'sqlplus'} -version"
                    output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
                    for line in output.split('\n'):
                        if 'Release' in line:
                            result['version'] = line.strip()
                            break
            except:
                pass
        else:
            # Check if sqlplus is in PATH
            if shutil.which('sqlplus'):
                result['installed'] = True
                result['binaries']['sqlplus'] = True
                result['oracle_home'] = 'FOUND_IN_PATH'
        
        return result
    
    def detect_database(self) -> Dict:
        """Detect database instance"""
        result = {
            'running': False,
            'instances': [],
            'current_sid': self.oracle_sid,
            'processes': {
                'pmon': [],
                'smon': [],
                'dbwr': [],
                'lgwr': [],
                'ckpt': [],
                'arch': [],
                'reco': []
            }
        }
        
        # Check for Oracle processes
        try:
            ps_output = subprocess.check_output(
                ['ps', 'aux'], 
                text=True, 
                stderr=subprocess.DEVNULL
            )
            
            for line in ps_output.split('\n'):
                # PMON processes indicate running instances
                if 'ora_pmon_' in line.lower():
                    sid = line.split('ora_pmon_')[1].split()[0]
                    result['instances'].append(sid)
                    result['running'] = True
                    result['processes']['pmon'].append(line.strip())
                
                # Other background processes
                if 'ora_smon_' in line.lower():
                    result['processes']['smon'].append(line.strip())
                if 'ora_dbw' in line.lower():
                    result['processes']['dbwr'].append(line.strip())
                if 'ora_lgwr_' in line.lower():
                    result['processes']['lgwr'].append(line.strip())
                if 'ora_ckpt_' in line.lower():
                    result['processes']['ckpt'].append(line.strip())
                if 'ora_arc' in line.lower():
                    result['processes']['arch'].append(line.strip())
                if 'ora_reco_' in line.lower():
                    result['processes']['reco'].append(line.strip())
        except:
            pass
        
        return result
    
    def detect_listener(self) -> Dict:
        """Detect TNS Listener"""
        result = {
            'running': False,
            'listeners': [],
            'ports': []
        }
        
        try:
            ps_output = subprocess.check_output(
                ['ps', 'aux'], 
                text=True, 
                stderr=subprocess.DEVNULL
            )
            
            for line in ps_output.split('\n'):
                if 'tnslsnr' in line.lower():
                    result['running'] = True
                    result['listeners'].append(line.strip())
        except:
            pass
        
        # Try to get listener status
        if shutil.which('lsnrctl'):
            try:
                lsnr_output = subprocess.check_output(
                    ['lsnrctl', 'status'],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                # Parse for ports
                for line in lsnr_output.split('\n'):
                    if 'PORT=' in line:
                        try:
                            port = line.split('PORT=')[1].split(')')[0]
                            result['ports'].append(port)
                        except:
                            pass
            except:
                pass
        
        return result
    
    def detect_grid_infrastructure(self) -> Dict:
        """Detect Grid Infrastructure"""
        result = {
            'installed': False,
            'running': False,
            'grid_home': None,
            'version': None
        }
        
        grid_home = os.environ.get('GRID_HOME', '/u01/app/19.3.0/grid')
        if Path(grid_home).exists():
            result['installed'] = True
            result['grid_home'] = grid_home
        
        # Check for Grid processes
        try:
            ps_output = subprocess.check_output(
                ['ps', 'aux'],
                text=True,
                stderr=subprocess.DEVNULL
            )
            if 'ocssd.bin' in ps_output or 'crsd.bin' in ps_output:
                result['running'] = True
        except:
            pass
        
        return result
    
    def detect_asm(self) -> Dict:
        """Detect ASM"""
        result = {
            'installed': False,
            'running': False,
            'instances': [],
            'disk_groups': []
        }
        
        try:
            ps_output = subprocess.check_output(
                ['ps', 'aux'],
                text=True,
                stderr=subprocess.DEVNULL
            )
            
            for line in ps_output.split('\n'):
                if 'asm_pmon_' in line.lower():
                    sid = line.split('asm_pmon_')[1].split()[0]
                    result['instances'].append(sid)
                    result['running'] = True
                    result['installed'] = True
        except:
            pass
        
        # Try to get disk groups
        if result['running'] and shutil.which('asmcmd'):
            try:
                dg_output = subprocess.check_output(
                    ['asmcmd', 'lsdg'],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                for line in dg_output.split('\n')[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            result['disk_groups'].append(parts[0])
            except:
                pass
        
        return result
    
    def detect_cluster(self) -> Dict:
        """Detect RAC cluster configuration"""
        result = {
            'configured': False,
            'nodes': [],
            'scan': None,
            'vip': []
        }
        
        # Check for cluster config file
        cluster_config = Path.home() / '.oracledba' / 'cluster.yaml'
        if cluster_config.exists():
            result['configured'] = True
            try:
                import yaml
                with open(cluster_config) as f:
                    config = yaml.safe_load(f)
                    result['nodes'] = config.get('nodes', [])
                    result['scan'] = config.get('scan', None)
                    result['vip'] = config.get('vip', [])
            except:
                pass
        
        return result
    
    def detect_features(self) -> Dict:
        """Detect enabled Oracle features"""
        features = {
            'archivelog': {'enabled': False, 'can_enable': False},
            'fra': {'enabled': False, 'can_enable': False},
            'flashback': {'enabled': False, 'can_enable': False},
            'rman': {'enabled': False, 'can_enable': False},
            'dataguard': {'enabled': False, 'can_enable': False},
            'multiplexing': {
                'controlfile': {'enabled': False, 'copies': 0},
                'redolog': {'enabled': False, 'members_per_group': 0}
            }
        }
        
        # Features require running database
        if not self.detect_database()['running']:
            return features
        
        # All features can potentially be enabled if DB is running
        for feature in ['archivelog', 'fra', 'flashback', 'rman', 'dataguard']:
            features[feature]['can_enable'] = True
        
        # Try to detect actual status via SQL*Plus
        if shutil.which('sqlplus'):
            try:
                # Check ARCHIVELOG mode
                sql = "SELECT log_mode FROM v$database;"
                result = self._run_sql(sql)
                if 'ARCHIVELOG' in result:
                    features['archivelog']['enabled'] = True
                
                # Check FRA
                sql = "SELECT value FROM v$parameter WHERE name='db_recovery_file_dest';"
                result = self._run_sql(sql)
                if result and result.strip() and 'no rows' not in result.lower():
                    features['fra']['enabled'] = True
                
                # Check Flashback
                sql = "SELECT flashback_on FROM v$database;"
                result = self._run_sql(sql)
                if 'YES' in result:
                    features['flashback']['enabled'] = True
                
                # Check multiplexing
                sql = "SELECT COUNT(*) FROM v$controlfile;"
                result = self._run_sql(sql)
                try:
                    count = int(result.strip().split('\n')[-1].strip())
                    if count > 1:
                        features['multiplexing']['controlfile']['enabled'] = True
                        features['multiplexing']['controlfile']['copies'] = count
                except:
                    pass
                
                sql = "SELECT COUNT(DISTINCT member) FROM v$logfile GROUP BY group# ORDER BY group#;"
                result = self._run_sql(sql)
                if result:
                    try:
                        members = [int(x.strip()) for x in result.strip().split('\n') if x.strip().isdigit()]
                        if members and max(members) > 1:
                            features['multiplexing']['redolog']['enabled'] = True
                            features['multiplexing']['redolog']['members_per_group'] = max(members)
                    except:
                        pass
            
            except:
                pass
        
        return features
    
    def _run_sql(self, sql: str, timeout: int = 10) -> str:
        """Run SQL query and return result"""
        try:
            cmd = f"sqlplus -S / as sysdba <<EOF\nSET PAGESIZE 0 FEEDBACK OFF VERIFY OFF HEADING OFF ECHO OFF\n{sql}\nEXIT;\nEOF"
            result = subprocess.check_output(
                cmd,
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=timeout
            )
            return result
        except:
            return ""
    
    def get_oracle_metrics(self) -> Dict:
        """Get detailed Oracle metrics (SGA, PGA, processes, etc.)"""
        metrics = {
            'sga': {},
            'pga': {},
            'memory': {},
            'processes': {},
            'sessions': {},
            'tablespaces': [],
            'datafiles': [],
            'tempfiles': []
        }
        
        if not self.detect_database()['running']:
            return metrics
        
        if not shutil.which('sqlplus'):
            return metrics
        
        try:
            # SGA Info
            sql = "SELECT name, value/1024/1024 as mb FROM v$sga;"
            result = self._run_sql(sql)
            for line in result.split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            metrics['sga'][parts[0]] = f"{float(parts[-1]):.2f} MB"
                        except:
                            pass
            
            # PGA Info
            sql = "SELECT name, value/1024/1024 as mb FROM v$pgastat WHERE name IN ('total PGA allocated', 'total PGA inuse');"
            result = self._run_sql(sql)
            for line in result.split('\n'):
                if 'PGA' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            key = ' '.join(parts[:-1])
                            metrics['pga'][key] = f"{float(parts[-1]):.2f} MB"
                        except:
                            pass
            
            # Process count
            sql = "SELECT COUNT(*) FROM v$process;"
            result = self._run_sql(sql)
            try:
                metrics['processes']['current'] = int(result.strip().split('\n')[-1].strip())
            except:
                pass
            
            # Session count
            sql = "SELECT COUNT(*) FROM v$session;"
            result = self._run_sql(sql)
            try:
                metrics['sessions']['current'] = int(result.strip().split('\n')[-1].strip())
            except:
                pass
            
            # Tablespace info
            sql = """
            SELECT df.tablespace_name,
                   ROUND(df.bytes/1024/1024, 2) as total_mb,
                   ROUND((df.bytes - NVL(fs.bytes, 0))/1024/1024, 2) as used_mb,
                   ROUND(NVL(fs.bytes, 0)/1024/1024, 2) as free_mb,
                   ROUND((1 - NVL(fs.bytes, 0)/df.bytes)*100, 2) as pct_used
            FROM (SELECT tablespace_name, SUM(bytes) bytes FROM dba_data_files GROUP BY tablespace_name) df
            LEFT JOIN (SELECT tablespace_name, SUM(bytes) bytes FROM dba_free_space GROUP BY tablespace_name) fs
            ON df.tablespace_name = fs.tablespace_name
            ORDER BY df.tablespace_name;
            """
            result = self._run_sql(sql)
            for line in result.split('\n'):
                if line.strip() and not line.startswith('---'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            metrics['tablespaces'].append({
                                'name': parts[0],
                                'total_mb': float(parts[1]),
                                'used_mb': float(parts[2]),
                                'free_mb': float(parts[3]),
                                'pct_used': float(parts[4])
                            })
                        except:
                            pass
            
            # Datafile count
            sql = "SELECT COUNT(*) FROM v$datafile;"
            result = self._run_sql(sql)
            try:
                metrics['datafiles'] = int(result.strip().split('\n')[-1].strip())
            except:
                metrics['datafiles'] = 0
            
            # Tempfile count
            sql = "SELECT COUNT(*) FROM v$tempfile;"
            result = self._run_sql(sql)
            try:
                metrics['tempfiles'] = int(result.strip().split('\n')[-1].strip())
            except:
                metrics['tempfiles'] = 0
        
        except Exception as e:
            print(f"Error getting metrics: {e}")
        
        return metrics
