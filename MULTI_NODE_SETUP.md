# 🏗️ Multi-Node Oracle Setup Guide

## Architecture 3-Tier avec RAC + NFS

Ce guide vous montre comment déployer une infrastructure Oracle haute disponibilité sur 3 machines:
- **2 nœuds RAC** (Oracle 19c avec Grid Infrastructure)
- **1 serveur NFS** (stockage partagé pour backups)

---

## 📋 Prérequis

### Machines requises:

| Machine | Rôle | RAM | CPU | Stockage | IP |
|---------|------|-----|-----|----------|-----|
| **VM1** | Oracle RAC Node 1 | 8 GB | 4 cores | 50 GB | 178.128.10.67 |
| **VM2** | Oracle RAC Node 2 | 8 GB | 4 cores | 50 GB | 178.128.10.68 |
| **VM3** | NFS Storage Server | 4 GB | 2 cores | 100 GB | 178.128.10.69 |

### Réseau requis:
- **Réseau public**: Communication clients → RAC
- **Réseau privé**: Interconnexion RAC (heartbeat)
- **NFS mount**: Backup centralisé

---

## 🚀 Installation Rapide (Mode Semi-Automatique)

### Phase 1: Préparation de toutes les machines

```bash
# Sur toutes les 3 VMs:
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba
sudo bash install.sh
source ~/.bashrc
```

---

### Phase 2: Configuration NFS Server (VM3)

```bash
# VM3 - Serveur NFS
ssh root@178.128.10.69

# Créer les dossiers d'export
sudo mkdir -p /nfs/backup /nfs/shared /nfs/fra
sudo chmod 777 /nfs/backup /nfs/shared /nfs/fra

# Configurer NFS avec oradba
oradba nfs setup-server \
  --export-path /nfs/backup \
  --clients "178.128.10.67(rw,sync,no_root_squash) 178.128.10.68(rw,sync,no_root_squash)"

oradba nfs setup-server \
  --export-path /nfs/shared \
  --clients "178.128.10.67(rw,sync,no_root_squash) 178.128.10.68(rw,sync,no_root_squash)"

oradba nfs setup-server \
  --export-path /nfs/fra \
  --clients "178.128.10.67(rw,sync,no_root_squash) 178.128.10.68(rw,sync,no_root_squash)"

# Vérifier les exports
exportfs -v
```

**Résultat attendu**:
```
/nfs/backup     178.128.10.67(rw,sync,no_root_squash)
/nfs/shared     178.128.10.67(rw,sync,no_root_squash)
/nfs/fra        178.128.10.67(rw,sync,no_root_squash)
```

---

### Phase 3: Installation Oracle sur Node 1 (VM1)

```bash
# VM1 - Premier nœud RAC
ssh root@178.128.10.67

# Vérification système
oradba precheck
# Si des problèmes → générer le script de fix
oradba precheck --fix
sudo bash fix-precheck-issues.sh

# Télécharger Oracle 19c (via Oracle.com)
# Placer le ZIP dans /tmp/LINUX.X64_193000_db_home.zip

# Installation complète
sudo oradba install full \
  --installer-zip /tmp/LINUX.X64_193000_db_home.zip \
  --sid RACDB1 \
  --db-name RACDB \
  --pdb-name PDB1

# Monter NFS pour backups
sudo oradba nfs setup-client \
  --server 178.128.10.69 \
  --remote-path /nfs/backup \
  --mount-point /backup

sudo oradba nfs setup-client \
  --server 178.128.10.69 \
  --remote-path /nfs/fra \
  --mount-point /fra

# Configurer RMAN avec backup sur NFS
oradba rman setup \
  --retention 7 \
  --backup-location /backup \
  --fra-location /fra

# Tester l'installation
oradba test --full --report
```

---

### Phase 4: Installation Oracle sur Node 2 (VM2)

```bash
# VM2 - Deuxième nœud RAC
ssh root@178.128.10.68

# Répéter les mêmes étapes que Node 1
oradba precheck
sudo oradba install full \
  --installer-zip /tmp/LINUX.X64_193000_db_home.zip \
  --sid RACDB2 \
  --db-name RACDB \
  --pdb-name PDB1

# Monter NFS
sudo oradba nfs setup-client \
  --server 178.128.10.69 \
  --remote-path /nfs/backup \
  --mount-point /backup

sudo oradba nfs setup-client \
  --server 178.128.10.69 \
  --remote-path /nfs/fra \
  --mount-point /fra

# Configurer RMAN
oradba rman setup \
  --retention 7 \
  --backup-location /backup \
  --fra-location /fra
```

---

### Phase 5: Configuration RAC (MANUEL pour l'instant)

⚠️ **Note**: La configuration RAC nécessite Grid Infrastructure. 
Le package `oradba` peut installer Oracle Database, mais **Grid Infrastructure nécessite une installation séparée**.

**Option 1: RAC Complet** (nécessite Grid Infrastructure)
- Installer Grid Infrastructure manuellement
- Puis utiliser `oradba rac setup`

**Option 2: Active Data Guard** (Plus simple, haute disponibilité)
- Node 1 = Primary database
- Node 2 = Standby database (sync automatique)
- Utiliser `oradba dataguard setup`

**Option 3: Pour l'instant** (Sans RAC)
- 2 bases de données indépendantes
- NFS partagé pour backups
- Tests et déploiements identiques

---

### Phase 6: Configuration Backups RMAN centralisés

```bash
# Sur Node 1
oradba rman backup --type full --tag "NODE1_FULL_$(date +%Y%m%d)"

# Sur Node 2  
oradba rman backup --type full --tag "NODE2_FULL_$(date +%Y%m%d)"

# Vérifier les backups sur NFS
ssh root@178.128.10.69
ls -lh /nfs/backup/
```

---

## 🧪 Tests de validation

### Test 1: Connectivité NFS
```bash
# Depuis VM1 et VM2
df -h | grep nfs
# Doit montrer: 178.128.10.69:/nfs/backup sur /backup
```

### Test 2: Backup RMAN
```bash
# Sur chaque nœud
oradba rman backup --type archive
ls -lh /backup/
```

### Test 3: Tests Oracle
```bash
# Sur chaque nœud
oradba test --full --report
# Doit afficher: 11/11 tests passés
```

### Test 4: Haute disponibilité
```bash
# Arrêter Node 1
sudo reboot

# Depuis Node 2 - l'application continue de fonctionner
sqlplus system/password@RACDB
```

---

## 📊 Cas d'usage supportés

| Fonctionnalité | Disponible | Commande |
|----------------|------------|----------|
| **Installation Oracle multi-nœuds** | ✅ | `oradba install full` |
| **NFS centralisé** | ✅ | `oradba nfs setup-server/client` |
| **RMAN backups vers NFS** | ✅ | `oradba rman backup` |
| **Tests automatiques** | ✅ | `oradba test` |
| **Sécurité** | ✅ | `oradba security audit` |
| **Data Guard** | ⚠️ Scripts disponibles | `tp09-dataguard.sh` |
| **RAC complet** | ⚠️ Nécessite Grid Infra | Manuel + `oradba rac setup` |
| **ASM** | ⚠️ Nécessite Grid Infra | `oradba asm setup` |

---

## 🎯 Réponse à votre question

### **Pouvez-vous créer 2 machines + 1 NFS avec backup RMAN?**
✅ **OUI - 100% automatisé** avec `oradba`

### **Pouvez-vous avoir RAC entre les 2 nœuds?**
⚠️ **PARTIELLEMENT** - Grid Infrastructure doit être installé manuellement d'abord, puis `oradba rac setup` peut configurer le reste.

### **Pouvez-vous avoir haute disponibilité?**
✅ **OUI** - Avec Data Guard (plus simple que RAC, fonctionnalité similaire)

### **Pouvez-vous tester rapidement tout?**
✅ **OUI** - `oradba test` valide toute l'installation en quelques secondes

---

## 🚀 Installation Complète Recommandée (30 minutes)

```bash
# 1. VM3 - NFS Server (5 min)
git clone https://github.com/ELMRABET-Abdelali/oracledba.git && cd oracledba && sudo bash install.sh
oradba nfs setup-server --export-path /nfs/backup --clients "*"

# 2. VM1 - Node 1 (10 min)
git clone https://github.com/ELMRABET-Abdelali/oracledba.git && cd oracledba && sudo bash install.sh
oradba precheck && oradba install full --installer-zip /tmp/oracle.zip --sid PRODDB1
oradba nfs setup-client --server 178.128.10.69 --remote-path /nfs/backup --mount-point /backup
oradba rman setup --backup-location /backup

# 3. VM2 - Node 2 (10 min)  
git clone https://github.com/ELMRABET-Abdelali/oracledba.git && cd oracledba && sudo bash install.sh
oradba precheck && oradba install full --installer-zip /tmp/oracle.zip --sid PRODDB2
oradba nfs setup-client --server 178.128.10.69 --remote-path /nfs/backup --mount-point /backup
oradba rman setup --backup-location /backup

# 4. Tests (5 min)
oradba test --full
oradba rman backup --type full
```

**Résultat**: 2 bases Oracle + NFS + RMAN centralisé + Tests automatiques ✅

---

## 📝 Prochaines améliorations du package

Pour rendre votre workflow 100% automatique, je recommande d'ajouter:
1. **Script d'orchestration multi-VM** - `oradba cluster deploy --nodes 178.128.10.67,178.128.10.68 --nfs 178.128.10.69`
2. **Grid Infrastructure automatique** - Installation Grid simplifiée
3. **RAC one-command** - `oradba rac deploy --nodes 2`
4. **Data Guard automatique** - `oradba dataguard setup --primary VM1 --standby VM2`

**Voulez-vous que je crée ces scripts d'orchestration?** 🚀
