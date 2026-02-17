# 🌐 OracleDBA Web GUI Guide

## Overview

The OracleDBA Web GUI provides a **complete browser-based interface** for managing Oracle databases. Execute all CLI commands through an intuitive dashboard with real-time monitoring and easy configuration.

## Features

### 🎯 Core Capabilities

- **Dashboard**: Real-time system status and health monitoring
- **Database Management**: Create, configure, and monitor databases
- **Storage Management**: Tablespaces, control files, redo logs
- **Data Protection**: ARCHIVELOG, FRA, RMAN backups, Flashback
- **Security**: User management, privileges, profiles, audit configuration
- **Cluster Management**: RAC, ASM, NFS, multi-node configuration
- **Sample Database**: Quick testing environment with pre-loaded data
- **Interactive Terminal**: Execute any oradba command via web interface

### 🔐 Security Features

- **Authentication**: Secure login with password protection
- **Session Management**: Automatic timeout after 1 hour
- **Password Policies**: Forced password change on first login
- **Role-Based Access**: Admin and user roles
- **Encrypted Storage**: Passwords hashed with SHA-256

## Quick Start

### 1. Installation

```bash
# Install web GUI dependencies
pip install -r requirements-gui.txt

# Or install individually
pip install flask flask-cors
```

### 2. Start the Web Server

```bash
# Start on default port 5000
oradba install gui

# Start on custom port
oradba install gui --port 8080

# Start on localhost only (more secure)
oradba install gui --host 127.0.0.1 --port 5000

# Enable debug mode (development only)
oradba install gui --debug
```

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

**Default credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **You will be forced to change this password on first login!**

## Usage Guide

### Dashboard

The main dashboard shows:

- **Oracle Installation Status**: Whether Oracle binaries are installed
- **Database Status**: Running or stopped (checks ora_pmon process)
- **Listener Status**: TNS listener running or stopped
- **Cluster Configuration**: RAC/NFS configuration status
- **Quick Actions**: Buttons for common tasks

**Auto-refresh**: Status updates automatically every 30 seconds

### Database Management

**Create New Database:**

1. Navigate to **Databases** section
2. Enter:
   - Database SID (e.g., PRODDB, TESTDB)
   - Memory allocation (minimum 1024 MB)
   - Character set (AL32UTF8 recommended)
3. Click **Create Database**
4. Monitor progress in the output terminal

**List Existing Databases:**

- Automatically loaded on page load
- Click **Refresh** to update the list

### Storage Management

**Create Tablespace:**

1. Go to **Storage** section
2. Enter tablespace name (e.g., USERS_DATA)
3. Specify size (100M, 1G, 5G, etc.)
4. Enable autoextend (recommended)
5. Click **Create Tablespace**

**Control File Multiplexing:**

- Click **Add Control File Copy** to add redundant control files
- Protects against control file corruption
- Recommended: 3 copies minimum

**Redo Log Multiplexing:**

- Click **Add Redo Log Member** to add redundant members
- Protects against redo log loss
- Recommended: 2 members per group minimum

### Data Protection

**Enable ARCHIVELOG Mode:**

1. Navigate to **Protection** section
2. Click **Enable** under ARCHIVELOG
3. Database will restart automatically
4. Status badge turns green when enabled

**Configure Fast Recovery Area (FRA):**

1. Click **Configure** under FRA
2. System will set:
   - Size: 10G (adjustable)
   - Location: /u01/fra
3. Stores all backups and archive logs

**RMAN Backup:**

1. Configure RMAN settings:
   - Retention days (default: 7)
   - Backup destination
   - Enable compression
2. Click **Apply Config**
3. Choose backup type:
   - **Full Backup**: Complete database
   - **Incremental**: Only changed blocks

**Flashback Database:**

1. Enter minutes to flashback (e.g., 60 for 1 hour ago)
2. Click **Flashback Database**
3. Confirms before execution

**Flashback Table:**

1. Enter table name (SCHEMA.TABLE_NAME)
2. Click **Flashback Table**
3. Recovers table to previous state

### Security Management

**Create Database User:**

1. Go to **Security** section
2. Enter:
   - Username (e.g., APP_USER)
   - Password
   - Default tablespace (USERS recommended)
   - Profile (secure_profile recommended)
3. Click **Create User**

**Grant Privileges:**

1. Enter username
2. Select privilege or role:
   - CONNECT: Login access
   - RESOURCE: Create objects
   - DBA: Full admin
   - CREATE SESSION, CREATE TABLE, etc.
3. Click **Grant**

**Create secure_profile:**

- Click **Create secure_profile** button
- Automatically configures:
  - Failed login attempts: 3
  - Password life time: 90 days
  - Password lock time: 1 day
  - Password reuse time: 365 days

**Configure Audit:**

1. Select audit action:
   - ALL: All statements
   - DDL: CREATE, ALTER, DROP
   - DML: INSERT, UPDATE, DELETE
   - SELECT: Query operations
   - LOGON: Login/logout events
2. Optionally specify user (leave empty for all users)
3. Click **Enable** or **Disable**
4. View audit records with **View Audit Records** button

### Cluster Management

**Add Cluster Node:**

1. Navigate to **Cluster** section
2. Enter:
   - Node name (e.g., rac2, storage1)
   - IP address
   - Node role (Database, Storage/NFS, Grid)
3. Enable SSH equivalence (recommended)
4. Click **Add Node**

**Configure NFS:**

1. Enter NFS server IP
2. Specify export path (e.g., /nfs/shared)
3. Set mount point (e.g., /mnt/nfs)
4. Click **Configure NFS**
5. Test connection with **Test NFS Connection**

**Grid Infrastructure:**

- Click **Install Grid** to setup Oracle Grid Infrastructure
- Takes 30-60 minutes
- Required for RAC and ASM

**ASM Configuration:**

- Click **Configure ASM** to setup Automatic Storage Management
- Shows disk groups and available disks

**SSH Equivalence:**

- Click **Setup for grid** or **Setup for oracle**
- Configures passwordless SSH between nodes
- Required for RAC operations

### Sample Database

**Create Sample Database:**

1. Go to **Sample DB** section
2. Click **Create Sample Database**
3. Wait 5-10 minutes for setup
4. Creates:
   - SAMPLEDB database
   - 3 tables with 6000+ rows
   - All protection features enabled
   - Security profiles configured

**Test Sample Database:**

- Click **Test Database** to validate all features
- Shows PASS/FAIL for each test

**Connection Info:**

- Click **Connection Info** to see:
  - SQL*Plus command
  - JDBC URL
  - Python cx_Oracle connection string

**Remove Sample Database:**

- Click **Remove Database**
- Confirms before deletion
- Completely removes all sample data

### Interactive Terminal

**Execute Commands:**

1. Navigate to **Terminal** section
2. Type any oradba command in the input field
3. Press Enter or click **Execute**
4. Output appears in terminal window

**Quick Commands:**

- Click any button to pre-fill common commands
- Saves typing for frequently used operations

**Command History:**

- All executed commands saved
- Click **Rerun** to execute again
- Up/Down arrows to navigate history

**Security Note:**

- Only `oradba` commands are allowed
- Shell commands blocked for security

## Configuration

### Server Configuration

Configuration stored in: `~/.oracledba/gui_config.json`

```json
{
  "port": 5000,
  "host": "0.0.0.0",
  "debug": false,
  "session_timeout": 3600,
  "oracle_home": "/u01/app/oracle/product/19.3.0/dbhome_1"
}
```

### User Management

Users stored in: `~/.oracledba/gui_users.json`

```json
{
  "admin": {
    "password_hash": "...",
    "role": "admin",
    "must_change_password": false
  }
}
```

**Add New User (Manual):**

```python
import hashlib
import json

users = json.load(open('~/.oracledba/gui_users.json'))
users['newuser'] = {
    'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
    'role': 'user',
    'must_change_password': True
}
json.dump(users, open('~/.oracledba/gui_users.json', 'w'), indent=2)
```

## Production Deployment

### Using Gunicorn (Linux)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
cd /path/to/oracledba
gunicorn -w 4 -b 0.0.0.0:5000 'oracledba.web_server:app'
```

### Using Waitress (Windows)

```bash
# Install waitress
pip install waitress

# Run server
cd C:\path\to\oracledba
waitress-serve --host=0.0.0.0 --port=5000 oracledba.web_server:app
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name oracledba.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/TLS (HTTPS)

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Run with SSL
python -c "
from oracledba.web_server import app
app.run(host='0.0.0.0', port=5000, 
        ssl_context=('cert.pem', 'key.pem'))
"
```

### Systemd Service (Linux)

Create `/etc/systemd/system/oracledba-gui.service`:

```ini
[Unit]
Description=OracleDBA Web GUI
After=network.target

[Service]
Type=simple
User=oracle
WorkingDirectory=/home/oracle
Environment="ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1"
ExecStart=/usr/bin/python3 -m oracledba.web_server
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oracledba-gui
sudo systemctl start oracledba-gui
sudo systemctl status oracledba-gui
```

## Security Best Practices

### 1. Change Default Password

**IMMEDIATELY** after first login, change the admin password to something strong.

### 2. Restrict Access

Run on localhost only for single-user systems:

```bash
oradba install gui --host 127.0.0.1
```

### 3. Use Firewall

Allow only trusted IPs:

```bash
# iptables example
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j DROP
```

### 4. Enable HTTPS

Use SSL/TLS for production deployments (see above)

### 5. Regular Backups

The GUI configuration and user database are in:
- `~/.oracledba/gui_config.json`
- `~/.oracledba/gui_users.json`

Back these up regularly!

### 6. Monitor Logs

Check for suspicious activity:

```bash
# Application logs
tail -f ~/.oracledba/gui.log

# System logs
journalctl -u oracledba-gui -f
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Use different port
oradba install gui --port 8080
```

### Cannot Connect from Other Machines

```bash
# Check firewall
sudo firewall-cmd --add-port=5000/tcp --permanent  # CentOS/RHEL
sudo ufw allow 5000  # Ubuntu

# Check host setting
oradba install gui --host 0.0.0.0  # Listen on all interfaces
```

### Oracle Not Detected

Make sure ORACLE_HOME is set:

```bash
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH
```

### Missing Dependencies

```bash
# Install all GUI dependencies
pip install -r requirements-gui.txt

# Or minimal install
pip install flask flask-cors
```

### Session Timeout

Default timeout is 1 hour. To change:

Edit `~/.oracledba/gui_config.json`:

```json
{
  "session_timeout": 7200
}
```

## API Endpoints

The GUI exposes REST API endpoints that can be used programmatically:

### System Status

```bash
curl http://localhost:5000/api/system-status
```

### Database Operations

```bash
# List databases
curl http://localhost:5000/api/databases/list

# Create database
curl -X POST http://localhost:5000/api/databases/create \
  -H "Content-Type: application/json" \
  -d '{"sid": "PRODDB", "memory": 2048}'
```

### Storage Operations

```bash
# List tablespaces
curl http://localhost:5000/api/storage/tablespaces

# Create tablespace
curl -X POST http://localhost:5000/api/storage/tablespace/create \
  -H "Content-Type: application/json" \
  -d '{"name": "USERS_DATA", "size": "1G"}'
```

### Security Operations

```bash
# List users
curl http://localhost:5000/api/security/users

# Create user
curl -X POST http://localhost:5000/api/security/user/create \
  -H "Content-Type: application/json" \
  -d '{"username": "APP_USER", "password": "SecurePass123"}'
```

## FAQ

### Q: Can I use the CLI and GUI at the same time?

**A:** Yes! They operate independently. Changes made in one are immediately available in the other.

### Q: Is the GUI secure for production use?

**A:** With proper configuration (HTTPS, firewall, strong passwords), yes. Follow the security best practices section above.

### Q: Can multiple users access the GUI simultaneously?

**A:** Yes, but currently all users share the same session. Role-based access control is planned for future releases.

### Q: Does the GUI work on Windows?

**A:** Yes, but Oracle Database 19c is not officially supported on Windows. The GUI itself works fine on Windows for development/testing.

### Q: Can I customize the GUI?

**A:** Yes! Templates are in `oracledba/web/templates/` and can be modified. Restart the server to see changes.

### Q: How do I update the GUI?

**A:** Pull the latest code and restart:

```bash
cd /path/to/oracledba
git pull
oradba install gui
```

## Support

For issues, feature requests, or questions:

1. Check the [main README](../README.md)
2. Review [FEATURES_GUIDE.md](../FEATURES_GUIDE.md)
3. Open an issue on GitHub
4. Check the terminal output for error messages

## Next Steps

1. ✅ Start the GUI: `oradba install gui`
2. ✅ Change default password
3. ✅ Create sample database for testing
4. ✅ Explore all features
5. ✅ Configure production security
6. ✅ Deploy with systemd/gunicorn

Happy database administration! 🎉
