# 🔧 Gestion Dynamique des Nœuds Oracle - Guide Complet

## 🎯 Vue d'ensemble

Le système de gestion de cluster permet de:
- ✅ **Ajouter/Supprimer des nœuds dynamiquement**
- ✅ **Stocker les clés SSH de manière sécurisée**
- ✅ **Gérer la configuration NFS centralisée**
- ✅ **Orchestrer les déploiements multi-machines**
- ✅ **Exporter l'inventaire pour Ansible/Terraform**

---

## 📁 **Où sont stockées les configurations?**

### Emplacement par défaut: `~/.oracledba/`

```
~/.oracledba/
├── cluster.yaml           # Configuration du cluster (nœuds, NFS, etc.)
├── ssh_keys/              # Clés SSH copiées et sécurisées
│   ├── node1_rsa          # Clé pour node1
│   ├── node2_rsa          # Clé pour node2
│   └── nfs1_rsa           # Clé pour serveur NFS
├── ansible_inventory.yaml # Export Ansible (optionnel)
└── cluster_export.yaml    # Export complet (optionnel)
```

### Contenu du fichier `cluster.yaml`:

```yaml
cluster_name: oracluster
created_at: '2026-02-16T23:00:00'
updated_at: '2026-02-16T23:15:00'

# Configuration globale
global_settings:
  oracle_base: /u01/app/oracle
  oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
  backup_location: /backup
  fra_location: /fra

# Nœuds du cluster
nodes:
  node1:
    ip: 178.128.10.67
    role: database
    ssh_user: root
    ssh_key: node1_rsa
    sid: PRODDB1
    oracle_base: /u01/app/oracle
    oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
    status: registered
    added_at: '2026-02-16T23:00:00'
    oracledba_installed: true
    nfs_mounts:
      - nfs_server: nfs1
        remote_path: /nfs/backup
        mount_point: /backup
        configured_at: '2026-02-16T23:05:00'
  
  node2:
    ip: 178.128.10.68
    role: database
    ssh_user: root
    ssh_key: node2_rsa
    sid: PRODDB2
    status: registered
    added_at: '2026-02-16T23:01:00'
  
  nfs1:
    ip: 178.128.10.69
    role: nfs
    ssh_user: root
    ssh_key: nfs1_rsa
    status: registered
    added_at: '2026-02-16T23:02:00'

# Serveurs NFS
nfs_servers:
  nfs1:
    ip: 178.128.10.69
    export_paths:
      - /nfs/backup
      - /nfs/fra
      - /nfs/shared
    clients:
      - 178.128.10.67
      - 178.128.10.68

# Références aux clés SSH
ssh_keys:
  node1: /home/user/.oracledba/ssh_keys/node1_rsa
  node2: /home/user/.oracledba/ssh_keys/node2_rsa
  nfs1: /home/user/.oracledba/ssh_keys/nfs1_rsa
```

---

## 🚀 **Commandes de gestion de cluster**

### 1. **Ajouter un nœud database**

```bash
# Ajouter Node1 avec sa clé SSH
oradba cluster add-node \
  --name node1 \
  --ip 178.128.10.67 \
  --role database \
  --ssh-key ~/.ssh/id_rsa \
  --ssh-user root \
  --sid PRODDB1

# Résultat:
# ✓ SSH key copied: /home/user/.oracledba/ssh_keys/node1_rsa
# → Testing SSH connection to 178.128.10.67...
# ✓ Node node1 added successfully
```

**Ce qui se passe**:
1. Copie votre clé SSH dans `~/.oracledba/ssh_keys/node1_rsa`
2. Sécurise la clé (chmod 600)
3. Teste la connexion SSH
4. Enregistre la configuration dans `cluster.yaml`

### 2. **Ajouter un serveur NFS**

```bash
# Ajouter NFS server avec exports
oradba cluster add-nfs \
  --name nfs1 \
  --ip 178.128.10.69 \
  --exports "/nfs/backup,/nfs/fra,/nfs/shared" \
  --ssh-key ~/.ssh/id_rsa

# Résultat:
# ✓ SSH key copied: /home/user/.oracledba/ssh_keys/nfs1_rsa
# ✓ NFS server nfs1 configured
```

### 3. **Lister tous les nœuds**

```bash
# Lister tous les nœuds
oradba cluster list

# Filtrer par rôle
oradba cluster list --role database
oradba cluster list --role nfs

# Résultat:
# ┏━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
# ┃ Name  ┃ IP             ┃ Role     ┃ SID     ┃ SSH User ┃ Status   ┃
# ┡━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
# │ node1 │ 178.128.10.67  │ database │ PRODDB1 │ root     │ registered│
# │ node2 │ 178.128.10.68  │ database │ PRODDB2 │ root     │ registered│
# │ nfs1  │ 178.128.10.69  │ nfs      │ -       │ root     │ registered│
# └───────┴────────────────┴──────────┴─────────┴──────────┴──────────┘
# Total nodes: 3
# Config location: /home/user/.oracledba/cluster.yaml
```

### 4. **Afficher les détails d'un nœud**

```bash
oradba cluster show node1

# Résultat:
# Node: node1
# IP Address: 178.128.10.67
# Role: database
# SSH User: root
# SSH Key: node1_rsa
# Status: registered
# Oracle SID: PRODDB1
# Oracle Home: /u01/app/oracle/product/19.3.0/dbhome_1
# Added: 2026-02-16T23:00:00
```

### 5. **Configurer un mount NFS**

```bash
# Monter /nfs/backup de nfs1 sur node1:/backup
oradba cluster mount-nfs \
  --node node1 \
  --nfs-server nfs1 \
  --remote-path /nfs/backup \
  --mount-point /backup

# Résultat:
# ✓ NFS mount configured: node1:/backup -> nfs1:/nfs/backup
```

**Cela enregistre la configuration**, mais ne fait PAS le mount réel.
Pour exécuter le mount:
```bash
oradba cluster ssh node1 "mount -t nfs nfs1:/nfs/backup /backup"
```

### 6. **Déployer OracleDBA sur un nœud**

```bash
# Déployer le package sur node1
oradba cluster deploy node1

# Ce qui se passe:
# 1. SSH vers node1
# 2. git clone https://github.com/ELMRABET-Abdelali/oracledba.git
# 3. cd oracledba && sudo bash install.sh
# 4. Marque le nœud comme "oracledba_installed: true"
```

### 7. **Exécuter des commandes SSH sur un nœud**

```bash
# Commande simple
oradba cluster ssh node1 "df -h"

# Commande avec sudo
oradba cluster ssh node1 "sudo systemctl status oracle"

# Multiple commandes
oradba cluster ssh node1 "source ~/.bashrc && oradba test"
```

**Le système utilise automatiquement**:
- L'IP du nœud
- L'utilisateur SSH configuré
- La clé SSH stockée dans `~/.oracledba/ssh_keys/`

### 8. **Supprimer un nœud**

```bash
# Supprimer avec confirmation
oradba cluster remove-node node2

# Supprimer sans confirmation
oradba cluster remove-node node2 --force

# Résultat:
# ✓ Node node2 removed from cluster
# (La clé SSH est aussi supprimée de ~/.oracledba/ssh_keys/)
```

⚠️ **IMPORTANT**: Cela supprime SEULEMENT la configuration du cluster.
L'Oracle et la machine physique ne sont **PAS affectés**.

### 9. **Exporter l'inventaire**

```bash
# Export YAML
oradba cluster export --format yaml
# → Crée: ~/.oracledba/cluster_export.yaml

# Export Ansible Inventory
oradba cluster export --format ansible
# → Crée: ~/.oracledba/ansible_inventory.yaml

# Utilisation avec Ansible:
ansible -i ~/.oracledba/ansible_inventory.yaml database_nodes -m ping
```

---

## 🔐 **Gestion des clés SSH**

### Sécurité des clés:

1. **Les clés sont copiées localement** dans `~/.oracledba/ssh_keys/`
2. **Permissions automatiques**: `chmod 600` sur chaque clé
3. **Séparation par nœud**: Chaque nœud a sa propre clé
4. **Aucune clé en clair dans cluster.yaml**: Seulement les références

### Format des clés stockées:

```bash
ls -l ~/.oracledba/ssh_keys/
# -rw------- 1 user user 1675 Feb 16 23:00 node1_rsa
# -rw------- 1 user user 1675 Feb 16 23:01 node2_rsa
# -rw------- 1 user user 1675 Feb 16 23:02 nfs1_rsa
```

### Utiliser une clé différente pour chaque nœud:

```bash
# Node1 avec clé spécifique
oradba cluster add-node --name node1 --ip 10.0.0.1 --ssh-key ~/.ssh/node1_key

# Node2 avec une autre clé
oradba cluster add-node --name node2 --ip 10.0.0.2 --ssh-key ~/.ssh/node2_key

# NFS avec clé commune
oradba cluster add-nfs --name nfs1 --ip 10.0.0.3 --ssh-key ~/.ssh/common_key
```

---

## 📝 **Workflow complet - Exemple pratique**

### **Scénario**: Déployer 2 nœuds Oracle + 1 NFS depuis zéro

```bash
# ÉTAPE 1: Ajouter les machines au cluster
echo "=== ENREGISTREMENT DES NŒUDS ==="

oradba cluster add-node \
  --name node1 \
  --ip 178.128.10.67 \
  --role database \
  --ssh-key ~/.ssh/id_rsa \
  --sid PRODDB1

oradba cluster add-node \
  --name node2 \
  --ip 178.128.10.68 \
  --role database \
  --ssh-key ~/.ssh/id_rsa \
  --sid PRODDB2

oradba cluster add-nfs \
  --name nfs1 \
  --ip 178.128.10.69 \
  --exports "/nfs/backup,/nfs/fra" \
  --ssh-key ~/.ssh/id_rsa

# Vérifier
oradba cluster list

# ÉTAPE 2: Déployer OracleDBA sur tous les nœuds
echo "=== DÉPLOIEMENT DU PACKAGE ==="

oradba cluster deploy node1
oradba cluster deploy node2
oradba cluster deploy nfs1

# ÉTAPE 3: Configurer NFS server (sur nfs1)
echo "=== CONFIGURATION NFS SERVER ==="

oradba cluster ssh nfs1 "
  mkdir -p /nfs/backup /nfs/fra
  chmod 777 /nfs/backup /nfs/fra
  
  cat > /etc/exports << EOF
/nfs/backup 178.128.10.67(rw,sync,no_root_squash) 178.128.10.68(rw,sync,no_root_squash)
/nfs/fra 178.128.10.67(rw,sync,no_root_squash) 178.128.10.68(rw,sync,no_root_squash)
EOF
  
  systemctl enable nfs-server
  systemctl start nfs-server
  exportfs -ra
"

# ÉTAPE 4: Enregistrer les mounts NFS dans la config
echo "=== ENREGISTREMENT MOUNTS NFS ==="

oradba cluster mount-nfs --node node1 --nfs-server nfs1 --remote-path /nfs/backup --mount-point /backup
oradba cluster mount-nfs --node node1 --nfs-server nfs1 --remote-path /nfs/fra --mount-point /fra

oradba cluster mount-nfs --node node2 --nfs-server nfs1 --remote-path /nfs/backup --mount-point /backup
oradba cluster mount-nfs --node node2 --nfs-server nfs1 --remote-path /nfs/fra --mount-point /fra

# ÉTAPE 5: Exécuter les mounts réels
echo "=== MONTAGE NFS ==="

oradba cluster ssh node1 "
  mkdir -p /backup /fra
  echo 'nfs1:/nfs/backup /backup nfs defaults 0 0' >> /etc/fstab
  echo 'nfs1:/nfs/fra /fra nfs defaults 0 0' >> /etc/fstab
  mount -a
  df -h | grep nfs
"

oradba cluster ssh node2 "
  mkdir -p /backup /fra
  echo 'nfs1:/nfs/backup /backup nfs defaults 0 0' >> /etc/fstab
  echo 'nfs1:/nfs/fra /fra nfs defaults 0 0' >> /etc/fstab
  mount -a
  df -h | grep nfs
"

# ÉTAPE 6: Installer Oracle sur les nœuds (nécessite Oracle ZIP)
echo "=== INSTALLATION ORACLE ==="

# Upload Oracle ZIP (si pas déjà présent)
# scp LINUX.X64_193000_db_home.zip root@178.128.10.67:/tmp/
# scp LINUX.X64_193000_db_home.zip root@178.128.10.68:/tmp/

oradba cluster ssh node1 "
  source ~/.bashrc
  oradba precheck
  # Installation manuelle ou via scripts
"

# ÉTAPE 7: Vérifier la configuration finale
echo "=== VÉRIFICATION FINALE ==="

oradba cluster list
oradba cluster show node1
oradba cluster show node2
oradba cluster show nfs1

# Export pour documentation
oradba cluster export --format yaml
oradba cluster export --format ansible
```

---

## 🎯 **Avantages du système**

### ✅ **Gestion centralisée**
- Toute la configuration dans `~/.oracledba/cluster.yaml`
- Pas besoin de se souvenir des IPs, clés SSH, SIDs
- `oradba cluster list` pour tout voir

### ✅ **Sécurité**
- Clés SSH copiées et sécurisées localement
- Permissions restrictives (600)
- Aucune clé en clair dans les fichiers de config

### ✅ **Flexibilité**
- Ajout/suppression de nœuds à la volée
- Support de plusieurs clés SSH différentes
- Rôles multiples: database, nfs, grid, standby

### ✅ **Automatisation**
- `oradba cluster deploy <node>` pour installer le package
- `oradba cluster ssh <node> <command>` pour exécuter des commandes
- Export Ansible pour orchestration avancée

### ✅ **Évolutivité**
- Démarrer avec 1 nœud
- Ajouter node2, node3... selon les besoins
- Ajouter/retirer des serveurs NFS
- Reconfigurer sans tout casser

---

## 📊 **Cas d'usage avancés**

### **Ajouter un 3ème nœud dynamiquement**

```bash
# Cluster actuel: node1, node2, nfs1
oradba cluster list

# Ajouter node3
oradba cluster add-node \
  --name node3 \
  --ip 178.128.10.70 \
  --role database \
  --ssh-key ~/.ssh/id_rsa \
  --sid PRODDB3

# Déployer OracleDBA
oradba cluster deploy node3

# Configurer NFS
oradba cluster mount-nfs --node node3 --nfs-server nfs1 --remote-path /nfs/backup --mount-point /backup

# Autoriser node3 sur NFS server
oradba cluster ssh nfs1 "
  echo '/nfs/backup 178.128.10.70(rw,sync,no_root_squash)' >> /etc/exports
  exportfs -ra
"

# Monter sur node3
oradba cluster ssh node3 "
  mkdir -p /backup
  echo 'nfs1:/nfs/backup /backup nfs defaults 0 0' >> /etc/fstab
  mount -a
"

# ✅ Node3 est maintenant intégré!
```

### **Supprimer un nœud (scale down)**

```bash
# Retirer node3 du cluster
oradba cluster remove-node node3 --force

# Nettoyer NFS (optionnel)
oradba cluster ssh nfs1 "
  sed -i '/178.128.10.70/d' /etc/exports
  exportfs -ra
"

# ✅ Node3 retiré proprement
```

---

## 🔧 **Maintenance du cluster**

### **Sauvegarder la configuration**

```bash
# Backup automatique à chaque modification
cp ~/.oracledba/cluster.yaml ~/.oracledba/cluster.yaml.backup

# Export pour archivage
oradba cluster export --format yaml
# Sauvegarde: ~/.oracledba/cluster_export.yaml
```

### **Restaurer une configuration**

```bash
# Restaurer depuis backup
cp ~/.oracledba/cluster.yaml.backup ~/.oracledba/cluster.yaml

# Vérifier
oradba cluster list
```

### **Migrer vers un nouveau poste de travail**

```bash
# Sur l'ancien poste
tar -czf oracledba-cluster-config.tar.gz ~/.oracledba/

# Sur le nouveau poste
tar -xzf oracledba-cluster-config.tar.gz -C ~/
oradba cluster list  # ✅ Tout est là!
```

---

## 🚀 **Prochaines fonctionnalités**

- [ ] `oradba cluster backup-config` - Backup automatique versionnée
- [ ] `oradba cluster sync` - Synchroniser la config avec les nœuds
- [ ] `oradba cluster health` - Vérifier l'état de tous les nœuds
- [ ] `oradba cluster upgrade` - Mettre à jour OracleDBA sur tous les nœuds
- [ ] `oradba cluster exec-all` - Exécuter une commande sur tous les nœuds

---

## 📚 **Résumé des commandes**

```bash
# Gestion des nœuds
oradba cluster add-node --name <name> --ip <ip> --role <role> --ssh-key <key>
oradba cluster remove-node <name> [--force]
oradba cluster list [--role <role>]
oradba cluster show <name>

# NFS
oradba cluster add-nfs --name <name> --ip <ip> --exports <paths> --ssh-key <key>
oradba cluster mount-nfs --node <node> --nfs-server <nfs> --remote-path <path> --mount-point <mount>

# Déploiement & Exécution
oradba cluster deploy <node>
oradba cluster ssh <node> "<command>"

# Export
oradba cluster export --format [yaml|ansible|terraform]
```

---

**La configuration du cluster est maintenant persistante, sécurisée et évolutive!** 🎉
