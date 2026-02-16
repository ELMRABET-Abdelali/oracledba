# 🚀 Cluster Management - Quick Reference

## 📦 **Configuration Storage**

```
~/.oracledba/
├── cluster.yaml              # Main cluster configuration
├── ssh_keys/                 # SSH keys (chmod 600)
│   ├── node1_rsa
│   ├── node2_rsa
│   └── nfs1_rsa
├── ansible_inventory.yaml    # Ansible export
└── cluster_export.yaml       # Full export
```

---

## ⚡ **Quick Commands**

### Add Database Node
```bash
oradba cluster add-node --name node1 --ip 178.128.10.67 \
  --role database --ssh-key ~/.ssh/id_rsa --sid PRODDB1
```

### Add NFS Server
```bash
oradba cluster add-nfs --name nfs1 --ip 178.128.10.69 \
  --exports "/nfs/backup,/nfs/fra" --ssh-key ~/.ssh/id_rsa
```

### List Nodes
```bash
oradba cluster list                    # All nodes
oradba cluster list --role database    # Filter by role
```

### Show Node Details
```bash
oradba cluster show node1
```

### Remove Node
```bash
oradba cluster remove-node node2          # With confirmation
oradba cluster remove-node node2 --force  # Skip confirmation
```

### Configure NFS Mount
```bash
oradba cluster mount-nfs --node node1 --nfs-server nfs1 \
  --remote-path /nfs/backup --mount-point /backup
```

### Deploy Package
```bash
oradba cluster deploy node1    # Installs OracleDBA on node1
```

### Execute Remote Command
```bash
oradba cluster ssh node1 "df -h"
oradba cluster ssh node1 "hostname && uptime"
```

### Export Inventory
```bash
oradba cluster export --format yaml       # Default export
oradba cluster export --format ansible    # Ansible inventory
oradba cluster export --format terraform  # Terraform format
```

---

## 📋 **30-Second Quick Start**

```bash
# 1. Add 2 database nodes + 1 NFS
oradba cluster add-node --name node1 --ip 10.0.0.1 --role database --ssh-key ~/.ssh/id_rsa --sid DB1
oradba cluster add-node --name node2 --ip 10.0.0.2 --role database --ssh-key ~/.ssh/id_rsa --sid DB2
oradba cluster add-nfs --name nfs1 --ip 10.0.0.3 --exports "/backup,/fra" --ssh-key ~/.ssh/id_rsa

# 2. Deploy OracleDBA to all
oradba cluster deploy node1
oradba cluster deploy node2

# 3. Configure NFS mounts
oradba cluster mount-nfs --node node1 --nfs-server nfs1 --remote-path /backup --mount-point /backup
oradba cluster mount-nfs --node node2 --nfs-server nfs1 --remote-path /backup --mount-point /backup

# 4. List configuration
oradba cluster list

# ✅ Done! Nodes managed from one place
```

---

## 🔐 **SSH Key Security**

✅ **Keys copied to**: `~/.oracledba/ssh_keys/{node}_rsa`  
✅ **Permissions**: Automatically set to `600` (secure)  
✅ **Per-node keys**: Each node can have different key  
✅ **No plaintext**: cluster.yaml only stores key references  

---

## 🎯 **Common Use Cases**

### Scale Up (Add node3)
```bash
oradba cluster add-node --name node3 --ip 10.0.0.4 --role database --ssh-key ~/.ssh/id_rsa --sid DB3
oradba cluster deploy node3
oradba cluster mount-nfs --node node3 --nfs-server nfs1 --remote-path /backup --mount-point /backup
```

### Scale Down (Remove node3)
```bash
oradba cluster remove-node node3 --force
```

### Health Check All Nodes
```bash
oradba cluster ssh node1 "uptime"
oradba cluster ssh node2 "uptime"
oradba cluster ssh nfs1 "df -h"
```

### Deploy Update to All
```bash
for node in node1 node2; do
  oradba cluster deploy $node
done
```

---

## 📂 **cluster.yaml Structure**

```yaml
cluster_name: oracluster
nodes:
  node1:
    ip: 178.128.10.67
    role: database
    ssh_key: node1_rsa          # → ~/.oracledba/ssh_keys/node1_rsa
    sid: PRODDB1
    nfs_mounts:
      - nfs_server: nfs1
        remote_path: /nfs/backup
        mount_point: /backup

nfs_servers:
  nfs1:
    ip: 178.128.10.69
    export_paths:
      - /nfs/backup
      - /nfs/fra
    clients:
      - 178.128.10.67
      - 178.128.10.68

ssh_keys:
  node1: /home/user/.oracledba/ssh_keys/node1_rsa
  node2: /home/user/.oracledba/ssh_keys/node2_rsa
```

---

## 🔧 **Troubleshooting**

### Can't connect to node
```bash
# Test SSH manually
ssh -i ~/.oracledba/ssh_keys/node1_rsa root@178.128.10.67

# Re-add node with correct key
oradba cluster remove-node node1 --force
oradba cluster add-node --name node1 --ip 178.128.10.67 --ssh-key /correct/path/to/key
```

### Config corrupted
```bash
# Restore from backup
cp ~/.oracledba/cluster.yaml.backup ~/.oracledba/cluster.yaml
oradba cluster list
```

### Missing permissions on keys
```bash
# Fix automatically by removing and re-adding
oradba cluster remove-node node1 --force
oradba cluster add-node --name node1 ... # Keys will be chmod 600 again
```

---

## 📚 **Full Documentation**

- [CLUSTER_MANAGEMENT.md](CLUSTER_MANAGEMENT.md) - Complete guide with examples
- [MULTI_NODE_SETUP.md](MULTI_NODE_SETUP.md) - Multi-node deployment procedure
- [ANSWER_MULTI_NODE.md](ANSWER_MULTI_NODE.md) - Architecture Q&A

---

**Configuration is stored in `~/.oracledba/` - portable and secure!** 🎉
