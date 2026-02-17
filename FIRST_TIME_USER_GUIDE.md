# 🚀 First Time User Guide

Welcome to OracleDBA! This guide will help you get started in **5 minutes**.

---

## 📋 Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher installed
- Git installed (to clone the repository)
- Internet connection (for dependencies)

Optional for full Oracle experience:
- Oracle Database 19c installed
- Rocky Linux 8/9 or CentOS (for Oracle installation)

---

## 🎯 Quick Start Path

Choose your path:

### Path 1: Web GUI Only (Recommended for Beginners)
**Time: 5 minutes**

### Path 2: CLI Only (For Terminal Users)
**Time: 3 minutes**

### Path 3: Full Experience (CLI + Web GUI + Oracle)
**Time: 2-3 hours**

---

## 🌐 Path 1: Web GUI Only

Perfect if you want to explore the interface without Oracle installed.

### Step 1: Clone the Repository
```bash
# Windows (PowerShell)
cd C:\Users\$env:USERNAME\Documents
git clone https://github.com/yourusername/oracledba.git
cd oracledba

# Linux/Mac
cd ~/projects
git clone https://github.com/yourusername/oracledba.git
cd oracledba
```

### Step 2: Install Package
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install the package
pip install -e .

# Install GUI dependencies
pip install -r requirements-gui.txt
```

### Step 3: Start the Web GUI
```bash
oradba install gui
```

You'll see:
```
══════════════════════════════════════════════════════════════
   🌐 OracleDBA Web GUI Server
══════════════════════════════════════════════════════════════

 Starting server on http://0.0.0.0:5000

 📋 Default credentials:
    Username: admin
    Password: admin123

 ⚠️  IMPORTANT: Change the default password after first login!

 Press Ctrl+C to stop the server

──────────────────────────────────────────────────────────────
 * Running on http://0.0.0.0:5000
──────────────────────────────────────────────────────────────
```

### Step 4: Open Your Browser
Navigate to: **http://localhost:5000**

### Step 5: Login
- **Username**: `admin`
- **Password**: `admin123`

You'll be prompted to change your password immediately.

### Step 6: Explore the Dashboard

You'll see the main dashboard with:
- ✅ **Oracle Installation**: Shows if Oracle is detected
- 🔴 **Database**: Shows status (will be "STOPPED" if no Oracle)
- 🔴 **Listener**: Shows status (will be "STOPPED" if no Oracle)
- 🔵 **Cluster**: Shows if cluster is configured

### Step 7: Try Terminal Commands
1. Click **"Interactive Terminal"** in the sidebar
2. Try these commands (they work even without Oracle):
   ```
   oradba help features
   oradba help quick
   oradba sample status
   ```

### Step 8: Explore All Pages
- **Database Management**: Create and manage databases
- **Storage Management**: Tablespaces, control files, redo logs
- **Data Protection**: ARCHIVELOG, FRA, RMAN, Flashback
- **Security Management**: Users, privileges, profiles, audit
- **Cluster Management**: Nodes, NFS, Grid Infrastructure, ASM
- **Sample Database**: Quick test environment

### ✅ Success!
You now have the Web GUI running. Most features require Oracle to be installed for full functionality.

---

## 💻 Path 2: CLI Only

Perfect for terminal power users.

### Step 1: Install
```bash
# Clone and install (same as Path 1, Steps 1-2)
git clone https://github.com/yourusername/oracledba.git
cd oracledba
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -e .
```

### Step 2: Explore Commands
```bash
# See all commands
oradba --help

# See help system
oradba help features

# See all 40+ features
oradba help feature all

# See quick commands
oradba help quick

# See workflow
oradba help workflow
```

### Step 3: Try Sample Commands
```bash
# These work without Oracle:
oradba help search backup
oradba help search cluster
oradba sample status
```

### ✅ Success!
You can now use all CLI commands. Oracle-specific commands require Oracle installation.

---

## 🏆 Path 3: Full Experience

The complete DBA journey with Oracle 19c.

### Phase 1: Prepare System (30 minutes)

#### On Rocky Linux 8/9 or CentOS:
```bash
# Clone repository
cd ~
git clone https://github.com/yourusername/oracledba.git
cd oracledba

# Install package
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements-gui.txt

# Run system preparation
oradba install system-prep

# Review what it did:
# - Disabled firewall and SELinux
# - Created oracle user/group
# - Set kernel parameters
# - Created directories
# - Configured limits
```

### Phase 2: Install Oracle (60 minutes)

#### Option A: Automatic Installation (Recommended)
```bash
# Download Oracle 19c installation files first
# Place them in: ~/oracle-installer/

# Run automatic installer
oradba install oracle-auto \
    --zip-file ~/oracle-installer/LINUX.X64_193000_db_home.zip \
    --base /u01/app/oracle \
    --create-sample-db

# This will:
# - Extract Oracle files
# - Install Oracle 19c
# - Create listener
# - Create PRODDB database
# - Takes 45-60 minutes
```

#### Option B: Use Pre-built Scripts
```bash
# Follow the TP (Travaux Pratiques) guides in order:
./tp01-system-readiness.sh    # System prep
./tp02-environment-setup.sh   # Environment variables
./tp03a-install-software.sh   # Oracle software
./tp03b-rocky8-dbca.sh        # Database creation
```

### Phase 3: Create Sample Database (10 minutes)

```bash
# Via CLI:
oradba sample create

# Or via Web GUI:
# 1. Start GUI: oradba install gui
# 2. Open browser: http://your-server-ip:5000
# 3. Login: admin / admin123
# 4. Navigate to: Sample Database
# 5. Click: Create Sample Database
# 6. Wait 5-10 minutes
```

The sample database includes:
- ✅ ARCHIVELOG mode enabled
- ✅ Fast Recovery Area configured (10GB)
- ✅ Control files multiplexed (3 copies)
- ✅ Redo logs multiplexed (2 members per group)
- ✅ Flashback enabled (24 hours retention)
- ✅ RMAN configured (7 days retention)
- ✅ Sample data (6000+ rows)
- ✅ Security profiles and users
- ✅ Audit enabled

### Phase 4: Explore All Features (30 minutes)

#### A. Via Web GUI
```bash
# Start GUI
oradba install gui --port 5000

# Open browser: http://your-server-ip:5000
```

**Try these actions:**
1. **Dashboard**: Watch real-time status updates
2. **Databases**: Create a new database
3. **Storage**: Create a tablespace, check multiplexing
4. **Protection**: Enable features, run RMAN backup
5. **Security**: Create users, grant privileges
6. **Cluster**: Add nodes, configure NFS
7. **Terminal**: Execute commands interactively

#### B. Via CLI
```bash
# Database operations
oradba database status
oradba database start
oradba database stop

# Storage operations
oradba storage tablespace create MYDATA 1G
oradba storage tablespace list

# Protection operations
oradba protection archivelog status
oradba rman backup full
oradba flashback database enable

# Security operations
oradba security user create testuser password123
oradba security grant testuser CONNECT
oradba security audit enable ALL

# Cluster operations
oradba cluster add-node rac2 192.168.1.102
oradba cluster nfs configure
```

### Phase 5: Test Complete Workflow (15 minutes)

Follow this realistic DBA scenario:

```bash
# 1. Morning check
oradba help workflow
# Shows: Check database → Check backups → Check alerts

# 2. Create production database
oradba database create PRODDB 4096  # 4GB memory

# 3. Configure protection
oradba protection archivelog enable
oradba protection fra configure
oradba flashback database enable

# 4. Create backup
oradba rman backup full

# 5. Create application user
oradba security user create app_owner password123
oradba security grant app_owner CONNECT
oradba security grant app_owner RESOURCE

# 6. Create tablespace
oradba storage tablespace create APP_DATA 5G

# 7. Test recovery
oradba sample create  # Create test data
oradba flashback table enable SAMPLEDB.CUSTOMERS

# 8. Setup monitoring
oradba tuning awr-report

# 9. Configure cluster (if multi-node)
oradba cluster add-node rac2 192.168.1.102
oradba cluster ssh-setup
oradba cluster nfs configure
```

### ✅ Phase 3 Complete!
You now have a fully functional Oracle DBA environment with all features enabled.

---

## 🎓 Learning Path

After completing your chosen path, follow this learning sequence:

### Week 1: Foundation
- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Explore all Web GUI pages
- [ ] Try 10 CLI commands
- [ ] Create sample database
- [ ] Test database features

### Week 2: Storage & Protection
- [ ] Read [TP04-Fichiers-Critiques.md](dba-story-tps/TP04-Fichiers-Critiques.md)
- [ ] Read [TP05-Gestion-Stockage.md](dba-story-tps/TP05-Gestion-Stockage.md)
- [ ] Practice tablespace creation
- [ ] Implement multiplexing
- [ ] Configure ARCHIVELOG
- [ ] Setup FRA

### Week 3: Backup & Recovery
- [ ] Read [TP07-Flashback.md](dba-story-tps/TP07-Flashback.md)
- [ ] Read [TP08-RMAN.md](dba-story-tps/TP08-RMAN.md)
- [ ] Configure RMAN
- [ ] Test full backup
- [ ] Test incremental backup
- [ ] Practice flashback recovery

### Week 4: Security & Performance
- [ ] Read [TP06-Securite-Acces.md](dba-story-tps/TP06-Securite-Acces.md)
- [ ] Read [TP10-Tuning.md](dba-story-tps/TP10-Tuning.md)
- [ ] Create users and roles
- [ ] Implement password policies
- [ ] Enable audit
- [ ] Generate AWR report
- [ ] Tune SQL queries

### Month 2: Advanced Features
- [ ] Data Guard (TP09)
- [ ] Multitenant (TP12)
- [ ] Patching (TP11)
- [ ] AI/ML Foundations (TP13)
- [ ] Concurrency (TP14)
- [ ] ASM & RAC (TP15)

---

## 🆘 Common Issues & Solutions

### Issue 1: "Port 5000 already in use"
**Solution:**
```bash
# Use different port
oradba install gui --port 8080

# Or find what's using port 5000
# Windows:
netstat -ano | findstr :5000
# Linux:
lsof -i :5000
```

### Issue 2: "Cannot connect to database"
**Solution:**
```bash
# Check if database is running
ps -ef | grep ora_pmon

# Check listener
ps -ef | grep tnslsnr

# Check environment variables
echo $ORACLE_HOME
echo $ORACLE_SID

# Source Oracle environment
source ~/.bash_profile
```

### Issue 3: "Module not found: flask"
**Solution:**
```bash
# Install GUI dependencies
pip install -r requirements-gui.txt

# Or install manually
pip install flask flask-cors
```

### Issue 4: "Permission denied" when installing Oracle
**Solution:**
```bash
# Ensure you're oracle user
whoami  # Should show "oracle"

# If not, switch:
sudo su - oracle

# Check directory permissions
ls -ld /u01/app/oracle
# Should be: drwxr-xr-x oracle oinstall
```

### Issue 5: "ORA-01034: ORACLE not available"
**Solution:**
```bash
# Set ORACLE_SID
export ORACLE_SID=PRODDB

# Start database
oradba database start

# Or manually
sqlplus / as sysdba
SQL> STARTUP
```

### Issue 6: Web GUI shows "Oracle Not Detected"
**Solution:**
```bash
# Check if ORACLE_HOME is set
echo $ORACLE_HOME

# Check if sqlplus exists
which sqlplus

# For Web GUI, ensure oracle user has proper environment
# Add to ~/.bashrc:
export ORACLE_HOME=/u01/app/oracle/product/19.0.0/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH
```

---

## 📚 Documentation Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [README.md](README.md) | Overview of entire project | Start here |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide | First time setup |
| [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md) | Complete Web GUI documentation | Using web interface |
| [WEB_GUI_IMPLEMENTATION.md](WEB_GUI_IMPLEMENTATION.md) | Technical details of GUI | Developers/customization |
| [FEATURES_GUIDE.md](FEATURES_GUIDE.md) | All 40+ features explained | Learning features |
| [COMPLETE_LEARNING_GUIDE.md](COMPLETE_LEARNING_GUIDE.md) | Step-by-step learning path | Structured learning |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture overview | Understanding internals |
| [TP01-TP15](dba-story-tps/) | Practical exercises (French) | Hands-on practice |

---

## 🎯 What to Do After Setup

### For Beginners:
1. **Explore Web GUI** - Click every button, try every feature
2. **Create Sample Database** - See everything working
3. **Follow TP Guides** - Hands-on exercises in French
4. **Use Help System** - `oradba help` is your friend
5. **Read Features Guide** - Understand what each feature does

### For Experienced DBAs:
1. **Production Deployment** - Follow WEB_GUI_GUIDE.md for Nginx setup
2. **Cluster Configuration** - Multi-node RAC setup
3. **Data Guard Setup** - Standby database configuration
4. **Performance Tuning** - AWR, SQL tuning, statistics
5. **Automation** - Use CLI in scripts

### For Developers:
1. **API Integration** - Use REST API endpoints
2. **Customization** - Modify templates and modules
3. **Extension** - Add new features to core modules
4. **Contributing** - Submit PRs to improve the project

---

## 🚀 Next Steps Checklist

### Immediate (Today):
- [ ] Complete Path 1, 2, or 3 above
- [ ] Change default password
- [ ] Explore Web GUI or CLI
- [ ] Read QUICKSTART.md
- [ ] Try `oradba help features`

### This Week:
- [ ] Create sample database
- [ ] Test 10 different features
- [ ] Read 3 TP guides
- [ ] Configure backups
- [ ] Create test users

### This Month:
- [ ] Complete all 15 TP exercises
- [ ] Setup production database
- [ ] Implement full backup strategy
- [ ] Configure monitoring
- [ ] Test disaster recovery

---

## 💡 Tips for Success

1. **Start Small**: Don't try to learn everything at once
2. **Use Help System**: `oradba help` is comprehensive
3. **Read TP Guides**: They provide realistic scenarios
4. **Practice Daily**: 30 minutes per day is better than 8 hours once
5. **Ask Questions**: Check documentation first, then ask community
6. **Document Your Work**: Keep notes of what you learn
7. **Test Everything**: Use sample database to experiment safely
8. **Join Community**: Share your experiences and learn from others

---

## 🎉 Welcome to OracleDBA!

You're now ready to become an Oracle Database professional. The platform provides:
- ✅ **60+ CLI commands** for automation
- ✅ **11 Web GUI pages** for visual management
- ✅ **40+ documented features** for comprehensive DBA work
- ✅ **15 practical exercises** for hands-on learning
- ✅ **Complete documentation** in English and French

**Choose your interface, follow your path, and enjoy your journey!** 🚀

---

**Need help?** Check the documentation or use `oradba help search <keyword>` to find what you need.
