#!/usr/bin/env python3
"""
OracleDBA Web GUI Server
Flask-based web interface for Oracle database administration
"""

import os
import sys
import json
import subprocess
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import secrets

# Import our CLI modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')
app.secret_key = secrets.token_hex(32)
CORS(app)

# Configuration
CONFIG_DIR = Path.home() / '.oracledba'
CONFIG_FILE = CONFIG_DIR / 'gui_config.json'
USERS_FILE = CONFIG_DIR / 'gui_users.json'

# Default admin credentials
DEFAULT_ADMIN = {
    'username': 'admin',
    'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),  # Change on first login
    'role': 'admin',
    'must_change_password': True
}


class GUIConfig:
    """GUI Configuration Manager"""
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.users_file = USERS_FILE
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create config directory and files if they don't exist"""
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Create default config
        if not self.config_file.exists():
            default_config = {
                'port': 5000,
                'host': '0.0.0.0',
                'debug': False,
                'session_timeout': 3600,  # 1 hour
                'oracle_home': os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1'),
                'created_at': datetime.now().isoformat()
            }
            self.save_config(default_config)
        
        # Create default users
        if not self.users_file.exists():
            self.save_users({'admin': DEFAULT_ADMIN})
    
    def load_config(self):
        """Load GUI configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config):
        """Save GUI configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_users(self):
        """Load users database"""
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def save_users(self, users):
        """Save users database"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)


config_manager = GUIConfig()


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            flash('Admin privileges required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = config_manager.load_users()
        
        if username in users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if users[username]['password_hash'] == password_hash:
                session['user'] = username
                session['role'] = users[username].get('role', 'user')
                session['login_time'] = datetime.now().isoformat()
                
                # Check if password change required
                if users[username].get('must_change_password'):
                    flash('Please change your password', 'warning')
                    return redirect(url_for('change_password'))
                
                flash(f'Welcome {username}!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('change_password.html')
        
        users = config_manager.load_users()
        username = session['user']
        
        # Verify current password
        current_hash = hashlib.sha256(current_password.encode()).hexdigest()
        if users[username]['password_hash'] != current_hash:
            flash('Current password incorrect', 'error')
            return render_template('change_password.html')
        
        # Update password
        users[username]['password_hash'] = hashlib.sha256(new_password.encode()).hexdigest()
        users[username]['must_change_password'] = False
        users[username]['password_changed_at'] = datetime.now().isoformat()
        config_manager.save_users(users)
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get system status
    status = get_system_status()
    return render_template('dashboard.html', status=status, user=session['user'])


@app.route('/api/system-status')
@login_required
def api_system_status():
    """API: Get system status"""
    return jsonify(get_system_status())


def get_system_status():
    """Get comprehensive system status"""
    status = {
        'hostname': subprocess.getoutput('hostname'),
        'timestamp': datetime.now().isoformat(),
        'oracle_home': os.environ.get('ORACLE_HOME', 'Not set'),
        'checks': {}
    }
    
    # Check Oracle installation
    oracle_home = os.environ.get('ORACLE_HOME')
    if oracle_home and os.path.exists(f"{oracle_home}/bin/sqlplus"):
        status['checks']['oracle_installed'] = True
        status['checks']['sqlplus_version'] = subprocess.getoutput(f"{oracle_home}/bin/sqlplus -v")
    else:
        status['checks']['oracle_installed'] = False
    
    # Check if database is running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        status['checks']['database_running'] = 'ora_pmon' in result.stdout
    except:
        status['checks']['database_running'] = False
    
    # Check listener
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        status['checks']['listener_running'] = 'tnslsnr' in result.stdout
    except:
        status['checks']['listener_running'] = False
    
    # Check cluster config
    cluster_config = CONFIG_DIR / 'cluster.yaml'
    status['checks']['cluster_configured'] = cluster_config.exists()
    
    return status


# ============================================================================
# DATABASE MANAGEMENT ROUTES
# ============================================================================

@app.route('/databases')
@login_required
def databases():
    """Database management page"""
    return render_template('databases.html')


@app.route('/api/databases/list')
@login_required
def api_databases_list():
    """API: List all databases"""
    try:
        result = execute_cli_command(['oradba', 'database', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/databases/create', methods=['POST'])
@login_required
def api_databases_create():
    """API: Create database"""
    data = request.json
    sid = data.get('sid', 'PRODDB')
    memory = data.get('memory', 2048)
    
    try:
        result = execute_cli_command(['oradba', 'database', 'create', '--sid', sid, '--memory', str(memory)])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# STORAGE MANAGEMENT ROUTES
# ============================================================================

@app.route('/storage')
@login_required
def storage():
    """Storage management page"""
    return render_template('storage.html')


@app.route('/api/storage/tablespaces')
@login_required
def api_storage_tablespaces():
    """API: List tablespaces"""
    try:
        result = execute_cli_command(['oradba', 'storage', 'tablespace', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/storage/tablespace/create', methods=['POST'])
@login_required
def api_storage_tablespace_create():
    """API: Create tablespace"""
    data = request.json
    name = data.get('name')
    size = data.get('size', '500M')
    
    try:
        result = execute_cli_command(['oradba', 'storage', 'tablespace', 'create', 
                                     '--name', name, '--size', size])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# PROTECTION ROUTES
# ============================================================================

@app.route('/protection')
@login_required
def protection():
    """Data protection page"""
    return render_template('protection.html')


@app.route('/api/protection/archivelog/status')
@login_required
def api_protection_archivelog_status():
    """API: ARCHIVELOG status"""
    try:
        result = execute_cli_command(['oradba', 'protection', 'archivelog', 'status'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/protection/archivelog/enable', methods=['POST'])
@login_required
def api_protection_archivelog_enable():
    """API: Enable ARCHIVELOG"""
    try:
        result = execute_cli_command(['oradba', 'protection', 'archivelog', 'enable'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/rman/backup', methods=['POST'])
@login_required
def api_rman_backup():
    """API: RMAN backup"""
    data = request.json
    backup_type = data.get('type', 'full')
    
    try:
        result = execute_cli_command(['oradba', 'rman', 'backup', backup_type])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# SECURITY ROUTES
# ============================================================================

@app.route('/security')
@login_required
def security():
    """Security management page"""
    return render_template('security.html')


@app.route('/api/security/users')
@login_required
def api_security_users():
    """API: List database users"""
    try:
        result = execute_cli_command(['oradba', 'security', 'user', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/security/user/create', methods=['POST'])
@login_required
def api_security_user_create():
    """API: Create database user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        result = execute_cli_command(['oradba', 'security', 'user', 'create',
                                     '--name', username, '--password', password])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# CLUSTER MANAGEMENT ROUTES
# ============================================================================

@app.route('/cluster')
@login_required
def cluster():
    """Cluster management page"""
    return render_template('cluster.html')


@app.route('/api/cluster/nodes')
@login_required
def api_cluster_nodes():
    """API: List cluster nodes"""
    try:
        result = execute_cli_command(['oradba', 'cluster', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/cluster/add-node', methods=['POST'])
@login_required
def api_cluster_add_node():
    """API: Add cluster node"""
    data = request.json
    name = data.get('name')
    ip = data.get('ip')
    role = data.get('role', 'database')
    
    try:
        result = execute_cli_command(['oradba', 'cluster', 'add-node',
                                     '--name', name, '--ip', ip, '--role', role])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# SAMPLE DATABASE ROUTES
# ============================================================================

@app.route('/sample')
@login_required
def sample():
    """Sample database page"""
    return render_template('sample.html')


@app.route('/api/sample/create', methods=['POST'])
@login_required
def api_sample_create():
    """API: Create sample database"""
    try:
        result = execute_cli_command(['oradba', 'sample', 'create'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sample/test', methods=['POST'])
@login_required
def api_sample_test():
    """API: Test sample database"""
    try:
        result = execute_cli_command(['oradba', 'sample', 'test'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# TERMINAL ROUTES
# ============================================================================

@app.route('/terminal')
@login_required
def terminal():
    """Interactive terminal page"""
    return render_template('terminal.html')


@app.route('/api/terminal/execute', methods=['POST'])
@login_required
def api_terminal_execute():
    """API: Execute command in terminal"""
    data = request.json
    command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    # Security: only allow oradba commands
    if not command.startswith('oradba '):
        return jsonify({'success': False, 'error': 'Only oradba commands are allowed'})
    
    try:
        result = execute_cli_command(command.split())
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def execute_cli_command(args, timeout=300):
    """Execute OracleDBA CLI command"""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n\nErrors:\n{result.stderr}"
        
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out after 5 minutes"
    except Exception as e:
        return f"Error executing command: {str(e)}"


# ============================================================================
# MAIN
# ============================================================================

def start_gui_server(port=5000, host='0.0.0.0', debug=False):
    """Start the GUI server"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🌐 OracleDBA Web GUI Server                         ║
║                                                          ║
║     Server running on: http://{host}:{port}         ║
║                                                          ║
║     Default credentials:                                 ║
║     Username: admin                                      ║
║     Password: admin123 (change on first login)           ║
║                                                          ║
║     Press Ctrl+C to stop                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_gui_server()
