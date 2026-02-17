# 🗄️ OracleDBA - Complete Oracle Database Administration Package

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Oracle 19c](https://img.shields.io/badge/Oracle-19c-red.svg)](https://www.oracle.com/database/)

Un package complet pour l'installation, la configuration et la gestion d'Oracle Database 19c sur Rocky Linux 8/9.

## 🚀 Fonctionnalités

### 🎯 Basé sur Scripts Testés Rocky Linux 8

Ce package est construit sur **15 scripts shell testés et approuvés** (TP01-TP15) couvrant l'intégralité du cycle de vie Oracle Database 19c. Consultez [SCRIPTS_MAPPING.md](SCRIPTS_MAPPING.md) pour la correspondance détaillée.

### ✨ Fonctionnalités Principales

- ✅ **Installation complète** d'Oracle 19c Enterprise Edition
- 🔧 **Configuration système** automatique (users, groups, kernel parameters)
- 💾 **RMAN** - Backups automatisés et récupération
- 🔄 **Data Guard** - Configuration standby database
- ⚡ **Performance Tuning** - Optimisation SQL et mémoire
- 🏢 **Multitenant** - Gestion CDB/PDB
- 💿 **ASM** - Automatic Storage Management
- 🔗 **RAC** - Real Application Clusters (concepts et setup)
- 🔐 **Sécurité** - Users, roles, privilèges
- 📊 **Flashback** - Technologies de récupération
- 🤖 **AI/ML** - Oracle Machine Learning
- 🌐 **NFS Setup** - Configuration serveur NFS pour RAC
- 🌐 **Web GUI** - Interface web complète pour toutes les opérations (NOUVEAU!)

### 🌐 Interface Web (NEW!)

**Gérez votre base Oracle depuis votre navigateur!**

```bash
# Installer les dépendances web
pip install -r requirements-gui.txt

# Démarrer l'interface web
oradba install gui

# Accéder dans votre navigateur
http://localhost:5000
```

**Fonctionnalités Web GUI:**
- ✅ Dashboard temps réel (statut Oracle, Database, Listener, Cluster)
- ✅ Gestion bases de données (création, configuration)
- ✅ Gestion stockage (tablespaces, control files, redo logs)
- ✅ Protection données (ARCHIVELOG, FRA, RMAN, Flashback)
- ✅ Sécurité (users, privilèges, profiles, audit)
- ✅ Gestion cluster (RAC, ASM, NFS, SSH)
- ✅ Base de données exemple (6000+ lignes, toutes fonctionnalités)
- ✅ Terminal interactif (exécution commandes CLI)

📖 **Voir [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md) et [QUICKSTART.md](QUICKSTART.md) pour plus de détails**

### 📦 15 TPs (Travaux Pratiques) Intégrés

Tous les scripts shell des TPs sont inclus et accessibles via CLI:

| TP | Module | Description |
|----|--------|-------------|
| **TP01** | `install system` | Préparation système (users, kernel, swap) |
| **TP02** | `install binaries` | Installation binaires Oracle 19c |
| **TP03** | `install database` | Création instance avec DBCA |
| **TP04** | `db multiplex-critical` | Multiplexage control files et redo logs |
| **TP05** | `db create-tablespace` | Gestion stockage et tablespaces |
| **TP06** | `security create-user` | Sécurité (users, rôles, profiles) |
| **TP07** | `flashback enable` | Flashback Database et Query |
| **TP08** | `rman backup` | RMAN backups (Full, Incrémental, Archive) |
| **TP09** | `dataguard setup-primary` | Data Guard Physical Standby |
| **TP10** | `tuning awr-report` | Performance Tuning et AWR |
| **TP11** | `patch apply` | Patching Oracle (RU, PSU) |
| **TP12** | `pdb create` | Multi-tenant CDB/PDB |
| **TP13** | `ai enable-auto-index` | AI Foundations et Auto-Indexing |
| **TP14** | `datapump export` | Data Pump et gestion locks |
| **TP15** | `rac check-cluster` | ASM et RAC Concepts |

📖 **Voir [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md) pour exemples détaillés de chaque TP**

## 📦 Installation

### Installation rapide via pip

```bash
pip install oracledba
```

### Installation depuis GitHub

```bash
git clone https://github.com/yourusername/oracledba.git
cd oracledba
pip install -e .
```

### Installation avec support Oracle

```bash
pip install oracledba[oracle]
```

## ⚡ Démarrage Rapide

### 1️⃣ Installation Oracle 19c Complète (Mode Automatique)

```bash
# 1. Télécharger et installer le package
git clone https://github.com/yourusername/oracledba.git
cd oracledba
pip install -e .

# 2. Préparer configuration
cp configs/default-config.yml ~/my-oracle-config.yml
vi ~/my-oracle-config.yml  # Personnaliser selon vos besoins

# 3. Installation complète en UNE commande (TP01+TP02+TP03)
sudo oradba install full --config ~/my-oracle-config.yml

# 4. Vérifier
oradba db status
sqlplus / as sysdba
```

**Résultat:** Base Oracle 19c opérationnelle en 20-30 minutes ! ✅

### 2️⃣ Exemples d'Utilisation Quotidienne

```bash
# Backup complet quotidien (TP08)
oradba rman backup --type full --tag DAILY_FULL

# Vérifier santé système (TP10)
oradba tuning health-check

# Créer nouvelle PDB (TP12)
oradba pdb create --name PDB_SALES --admin-user salesadm --admin-pass Sales123

# Export schema (TP14)
oradba datapump export --schema GDC_ADMIN --file /backup/gdc_admin.dmp

# Vérifier Data Guard synchronisation (TP09)
oradba dataguard status
```

### 3️⃣ Installation Pas-à-Pas (Mode Apprentissage)

Pour **comprendre chaque étape**, exécutez les scripts shell directement:

```bash
# TP01: Préparation système
sudo /usr/local/share/oracledba/scripts/tp01-system-readiness.sh

# TP02: Installation binaires
su - oracle
./tp02-installation-binaire.sh

# TP03: Création base
./tp03-creation-instance.sh

# Puis les autres TPs selon besoins...
```

### 4️⃣ Configuration Production avec Data Guard

```bash
# Sur PRIMARY:
oradba install full --config production-primary.yml
oradba dataguard setup-primary --standby-host standby.server.com

# Sur STANDBY:
oradba install full --config production-standby.yml --skip-database
oradba dataguard create-standby --primary-host primary.server.com

# Automatiser backups (crontab PRIMARY)
0 2 * * * /usr/local/bin/oradba rman backup --type full
0 */6 * * * /usr/local/bin/oradba rman backup --type incremental
```

📚 **Pour plus d'exemples, voir [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)**

## 🎯 Utilisation

### Installation complète d'Oracle 19c

```bash
# Installation interactive avec wizard
oradba-setup

# Installation complète automatique
oradba install --full

# Installation par étapes
oradba install --system          # Préparation système
oradba install --binaries        # Installation binaires Oracle
oradba install --database        # Création de la base de données
```

### Gestion des modules

```bash
# RMAN - Backup et Recovery
oradba rman --setup              # Configuration RMAN
oradba rman --backup full        # Backup complet
oradba rman --backup incremental # Backup incrémental
oradba rman --restore            # Restauration

# Data Guard
oradba dataguard --setup         # Configuration Data Guard
oradba dataguard --status        # Statut
oradba dataguard --switchover    # Switchover

# Performance Tuning
oradba tuning --analyze          # Analyse performance
oradba tuning --awr              # Rapport AWR
oradba tuning --addm             # ADDM Report
oradba tuning --sql-trace        # Traçage SQL

# ASM - Automatic Storage Management
oradba asm --setup               # Configuration ASM
oradba asm --create-diskgroup    # Créer diskgroup
oradba asm --status              # Statut ASM

# RAC - Real Application Clusters
oradba rac --setup               # Configuration RAC
oradba rac --add-node            # Ajouter nœud
oradba rac --status              # Statut cluster

# Multitenant (CDB/PDB)
oradba pdb --create NAME         # Créer PDB
oradba pdb --clone SRC DEST      # Cloner PDB
oradba pdb --list                # Lister PDBs
oradba pdb --open NAME           # Ouvrir PDB
oradba pdb --close NAME          # Fermer PDB

# Flashback
oradba flashback --enable        # Activer Flashback
oradba flashback --restore       # Restaurer avec Flashback

# Sécurité
oradba security --audit          # Configuration audit
oradba security --encryption     # Configurer TDE
oradba security --users          # Gestion users

# NFS Server
oradba nfs --setup               # Configuration NFS
oradba nfs --mount               # Monter NFS
oradba nfs --share               # Partager répertoire
```

### Gestion de base

```bash
# Statut de la base
oradba status

# Démarrer/Arrêter
oradba start
oradba stop
oradba restart

# Connecter à SQL*Plus
oradba sqlplus
oradba sqlplus --sysdba

# Logs et monitoring
oradba logs --alert              # Alert log
oradba logs --listener           # Listener log
oradba monitor --tablespaces     # Surveillance tablespaces
oradba monitor --sessions        # Sessions actives
```

### Scripts personnalisés

```bash
# Exécuter un script SQL
oradba exec script.sql

# Exécuter un script bash
oradba exec script.sh

# Exécuter des commandes RMAN
oradba rman --script backup.rman
```

## 📋 Configuration

### Fichier de configuration YAML

Créez un fichier `oradba-config.yml`:

```yaml
# Configuration OracleDBA
system:
  os: "Rocky Linux 8"
  min_ram_gb: 4
  min_disk_gb: 50

oracle:
  version: "19.3.0.0.0"
  edition: "EE"
  oracle_base: "/u01/app/oracle"
  oracle_home: "/u01/app/oracle/product/19.3.0/dbhome_1"

database:
  db_name: "GDCPROD"
  sid: "GDCPROD"
  cdb: true
  pdbs:
    - name: "PDB1"
      admin_password: "Oracle123"

backup:
  location: "/u01/backup"
  retention_days: 7
  compression: true

nfs:
  server: "192.168.1.10"
  export_path: "/u01/shared"
  mount_point: "/u01/nfs"
```

Utiliser la configuration:

```bash
oradba install --config oradba-config.yml
```

### Variables d'environnement

```bash
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib
```

## 🏗️ Architecture

```
oracledba/
├── oracledba/
│   ├── __init__.py
│   ├── cli.py                 # CLI principale
│   ├── setup_wizard.py        # Wizard d'installation
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── install.py         # Installation Oracle
│   │   ├── rman.py            # RMAN management
│   │   ├── dataguard.py       # Data Guard
│   │   ├── tuning.py          # Performance tuning
│   │   ├── asm.py             # ASM management
│   │   ├── rac.py             # RAC management
│   │   ├── pdb.py             # Multitenant
│   │   ├── flashback.py       # Flashback
│   │   ├── security.py        # Security
│   │   └── nfs.py             # NFS management
│   ├── scripts/               # Scripts bash/SQL
│   ├── configs/               # Configurations YAML
│   ├── templates/             # Templates Jinja2
│   └── utils/                 # Utilitaires
│       ├── logger.py
│       ├── oracle_client.py
│       └── ssh_client.py
├── tests/
├── docs/
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
└── requirements.txt
```

## 📚 Documentation Complète

### 🌟 Guides Principaux (Recommandés)

**[📖 Documentation Hub](docs/)** - Toute la documentation organisée

#### Pour Démarrer
- **[⚡ Quick Start](docs/guides/QUICKSTART.md)** - Démarrage rapide en 15 minutes
- **[📘 Guide d'Utilisation Complet](docs/guides/GUIDE_UTILISATION.md)** - Guide complet avec exemples pour TOUS les TPs (TP01-TP15)
  - Installation (3 méthodes: GitHub, PyPI, Script)
  - Configuration YAML détaillée
  - Exemples pratiques pour chaque chapitre (1300+ lignes)
  - Cas d'usage avancés (Production, Multi-PDB, Migration)
  - Section dépannage complète

#### Référence Rapide
- **[📋 Cheat Sheet](docs/reference/CHEAT_SHEET.md)** - Aide-mémoire des commandes essentielles
- **[🔄 Scripts Mapping](docs/guides/SCRIPTS_MAPPING.md)** - Correspondance scripts shell testés ↔️ CLI
- **[📄 Guide Installation](docs/reference/INSTALL.yml)** - Procédures d'installation détaillées

#### Pour Développeurs
- **[🔧 Developer Guide](docs/development/DEVELOPER_GUIDE.md)** - Architecture et contribution
- **[🤝 Contributing](docs/development/CONTRIBUTING.md)** - Comment contribuer

#### Pour Déploiement
- **[🚀 GitHub Publishing Guide](docs/deployment/GITHUB_GUIDE.md)** - Publier sur GitHub/PyPI
- **[📦 Package Summary](docs/deployment/PACKAGE_SUMMARY.md)** - Vue d'ensemble technique

### 📁 Exemples de Configuration

- [Configuration Production](examples/production-config.yml)
- [Configuration RAC](examples/rac-config.yml)
- [Script de vérification système](examples/system-check.sh)

### 📑 Autres Ressources

- [Changelog](CHANGELOG.md) - Historique des versions

## 🔧 Configuration VM et NFS

### Créer une nouvelle VM pour Oracle

```bash
# Sur la nouvelle VM
oradba vm-init --role database
oradba install --full --config mydb.yml

# Pour un nœud RAC
oradba vm-init --role rac-node --node-number 2
```

### Configuration NFS pour RAC

```bash
# Sur le serveur NFS
oradba nfs --setup-server --export /u01/shared

# Sur les clients RAC
oradba nfs --setup-client --server 192.168.1.10 --mount /u01/shared
```

## 🐳 Docker Support

```bash
# Builder l'image
docker build -t oracledba:latest .

# Lancer un conteneur
docker run -it --name oracle19c oracledba:latest

# Utiliser docker-compose
docker-compose up -d
```

## 📚 Documentation

Pour bien démarrer, consultez ces guides dans l'ordre:

### Getting Started
- **[FIRST_TIME_USER_GUIDE.md](FIRST_TIME_USER_GUIDE.md)** - Guide complet pour premiers utilisateurs (3 learning paths)
- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage rapide en 5 minutes

### Web GUI Documentation
- **[WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md)** - Guide complet d'utilisation de l'interface web
- **[WEB_GUI_IMPLEMENTATION.md](WEB_GUI_IMPLEMENTATION.md)** - Documentation technique de l'implémentation

### Technical Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture complète du système avec diagrammes visuels
- **[SESSION_COMPLETE_SUMMARY.md](SESSION_COMPLETE_SUMMARY.md)** - Résumé complet des fonctionnalités implémentées
- **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)** - Guide des 40+ fonctionnalités Oracle DBA

### Practical Exercises (Travaux Pratiques)
Les guides TP (Travaux Pratiques) se trouvent dans le dossier `dba-story-tps/`:
- **TP01-System-Readiness.md** - Préparation système
- **TP02-Installation-Binaire.md** - Installation Oracle
- **TP03-Creation-Instance.md** - Création d'instance
- **TP04-Fichiers-Critiques.md** - Multiplexage
- **TP05-Gestion-Stockage.md** - Tablespaces
- **TP06-Securite-Acces.md** - Sécurité
- **TP07-Flashback.md** - Flashback
- **TP08-RMAN.md** - Sauvegardes
- **TP09-Data-Guard.md** - Standby
- **TP10-Tuning.md** - Performance
- **TP11-Patching.md** - Patching
- **TP12-Multi-tenant.md** - CDB/PDB
- **TP13-AI-Foundations.md** - Intelligence artificielle
- **TP14-Mobilite-Concurrence.md** - Data Pump
- **TP15-ASM-RAC-Concepts.md** - Cluster

### Architecture et Concepts
Consultez [ARCHITECTURE.md](ARCHITECTURE.md) pour:
- Diagrammes d'architecture système
- Flux de données (CLI vs Web GUI)
- Structure des modules
- Cartes de couverture des fonctionnalités
- Options de déploiement
- Stack technologique

---

## 🧪 Tests

```bash
# Exécuter les tests
pytest

# Avec couverture
pytest --cov=oracledba

# Tests d'intégration
pytest tests/integration/
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **DBA Formation Team** - *Initial work*

## 🙏 Remerciements

- Oracle Corporation pour la documentation
- Rocky Linux Community
- Tous les contributeurs du projet

## 📞 Support

- 📧 Email: dba@formation.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/oracledba/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/oracledba/discussions)

## 📈 Roadmap

### Completed ✅
- [x] Interface web complète avec authentification
- [x] 60+ commandes CLI pour administration Oracle
- [x] Sample database avec 40+ fonctionnalités
- [x] Documentation complète (2000+ lignes)
- [x] 15 exercices pratiques (TP)

### In Progress 🚧
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD avec GitHub Actions

### Planned 📋
- [ ] Support pour Oracle 21c
- [ ] Monitoring en temps réel avec WebSocket
- [ ] Support Kubernetes (Operator pattern)
- [ ] Ansible playbooks pour déploiement
- [ ] Terraform modules pour infrastructure
- [ ] Support multi-cloud (AWS RDS, Azure, GCP)
- [ ] Interface mobile (Progressive Web App)
- [ ] Graphiques de performance interactifs
- [ ] Notifications par email/Slack
- [ ] Mode sombre (Dark mode)

---

⭐ Si ce projet vous aide, n'hésitez pas à lui donner une étoile sur GitHub !
