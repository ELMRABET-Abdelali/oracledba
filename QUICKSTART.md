# ⚡ OracleDBA Quick Start Guide

## 5-Minute Setup

### 1. Install (Choose One)

**Option A: Full Package**
```bash
git clone https://github.com/yourusername/oracledba.git
cd oracledba
pip install -e .
pip install -r requirements-gui.txt
```

**Option B: From PyPI (when published)**
```bash
pip install oracledba
pip install flask flask-cors
```

### 2. Start Web GUI

```bash
oradba install gui
```

Open browser: **http://localhost:5000**

Login:
- Username: `admin`
- Password: `admin123`

### 3. First Steps

1. **Change Password** (forced on first login)
2. **Create Sample Database** (Dashboard → Quick Actions → Create Sample Database)
3. **Explore Features** (Use sidebar navigation)

---

## Quick Command Reference

### Web GUI
```bash
# Start on default port 5000
oradba install gui

# Custom port
oradba install gui --port 8080

# Localhost only (secure)
oradba install gui --host 127.0.0.1
```

### Sample Database (via CLI)
```bash
# Create sample database with all features
oradba sample create

# Test all features
oradba sample test

# Show status
oradba sample status

# Remove
oradba sample remove
```

### Help System
```bash
# List all features
oradba help features

# Get detailed help
oradba help archivelog
oradba help rman-backup
oradba help dataguard

# Search features
oradba help search backup

# Show production workflow
oradba help workflow

# Quick reference
oradba help quick
```

### Database Management
```bash
# Create database
oradba database create --sid PRODDB --memory 2048

# Check status
oradba database status

# Start/stop
oradba database start --sid PRODDB
oradba database stop --sid PRODDB
```

### Data Protection
```bash
# Enable ARCHIVELOG
oradba protection archivelog enable

# Configure FRA
oradba protection fra configure --size 10G --dest /u01/fra

# Enable Flashback
oradba flashback database enable

# RMAN backup
oradba rman backup full
oradba rman backup incremental
```

### Security
```bash
# Create user
oradba security user create --name APP_USER --password SecurePass123

# Grant privileges
oradba security grant --user APP_USER --privilege CONNECT
oradba security grant --user APP_USER --privilege RESOURCE

# Create secure profile
oradba security profile create --name secure_profile

# Enable audit
oradba security audit enable --action DDL
```

### Cluster Management
```bash
# Add cluster node
oradba cluster add-node --name rac2 --ip 192.168.1.102 --role database

# Setup SSH
oradba cluster ssh-setup --user oracle

# Configure NFS
oradba cluster nfs configure --server 192.168.1.100 --export /nfs/shared

# List nodes
oradba cluster list
```

---

## Web GUI Navigation

### Main Sections

1. **Dashboard** - System status overview
2. **Databases** - Create and manage databases
3. **Storage** - Tablespaces, control files, redo logs
4. **Protection** - ARCHIVELOG, FRA, RMAN, Flashback
5. **Security** - Users, privileges, profiles, audit
6. **Cluster** - RAC, ASM, NFS, Grid Infrastructure
7. **Sample DB** - Testing environment
8. **Terminal** - Interactive command execution

### Quick Actions (Dashboard)

- **Create Sample Database** - 5-minute setup with all features
- **Manage Databases** - Create/configure databases
- **Configure Protection** - Enable ARCHIVELOG, RMAN, Flashback
- **Open Terminal** - Execute any command

---

## Common Workflows

### New Database Setup (Production)

**Via Web GUI:**
1. Dashboard → Manage Databases
2. Enter SID and memory
3. Click Create Database
4. Go to Protection → Enable ARCHIVELOG
5. Protection → Configure FRA
6. Protection → Enable Flashback
7. Protection → RMAN Full Backup

**Via CLI:**
```bash
oradba database create --sid PRODDB --memory 4096
oradba protection archivelog enable
oradba protection fra configure --size 20G
oradba flashback database enable
oradba rman backup full
```

### Learning Mode (Beginners)

1. **Start Web GUI**: `oradba install gui`
2. **Create Sample DB**: Dashboard → Create Sample Database
3. **Explore Features**: Use sidebar to visit each section
4. **Test Commands**: Terminal → Execute sample commands
5. **View Help**: `oradba help features`
6. **Follow Workflow**: `oradba help workflow`

### Daily DBA Tasks

**Via Web GUI:**
- Check Dashboard for system health
- Protection → RMAN Full Backup (weekly)
- Protection → RMAN Incremental (daily)
- Security → View Audit Records
- Storage → Monitor tablespace usage

**Via CLI:**
```bash
# Morning check
oradba database status
oradba sample status  # if using sample DB

# Daily backup
oradba rman backup incremental

# Check space
oradba storage tablespace list

# Monitor
oradba help quick  # reminder of all commands
```

---

## Useful Links

- **Complete Guide**: [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md)
- **All Features**: [FEATURES_GUIDE.md](FEATURES_GUIDE.md)
- **Learning Path**: [COMPLETE_LEARNING_GUIDE.md](COMPLETE_LEARNING_GUIDE.md)
- **Technical Docs**: [WEB_GUI_IMPLEMENTATION.md](WEB_GUI_IMPLEMENTATION.md)

---

## Troubleshooting

### "Port 5000 already in use"
```bash
# Use different port
oradba install gui --port 8080
```

### "Cannot connect from other machines"
```bash
# Check firewall
sudo firewall-cmd --add-port=5000/tcp --permanent

# Start on all interfaces
oradba install gui --host 0.0.0.0
```

### "Oracle not detected"
```bash
# Set ORACLE_HOME
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH
```

### "Missing dependencies"
```bash
# Install GUI dependencies
pip install flask flask-cors

# Or full requirements
pip install -r requirements-gui.txt
```

---

## Production Deployment

### Linux (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'oracledba.web_server:app'
```

### Systemd Service
```bash
sudo nano /etc/systemd/system/oracledba-gui.service
# (Copy config from WEB_GUI_GUIDE.md)

sudo systemctl enable oracledba-gui
sudo systemctl start oracledba-gui
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

---

## Security Checklist

- [ ] Change default admin password
- [ ] Use `--host 127.0.0.1` for local-only access
- [ ] Configure firewall to restrict access
- [ ] Use HTTPS in production (via Nginx)
- [ ] Regular backups of config files (`~/.oracledba/`)
- [ ] Monitor logs for suspicious activity
- [ ] Keep software up to date

---

## Next Steps

1. ✅ Install and start GUI
2. ✅ Create sample database
3. ✅ Explore all features
4. ✅ Read complete documentation
5. ✅ Deploy to production
6. ✅ Train your team

**You're ready to go! 🚀**

For detailed information, see [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md)
