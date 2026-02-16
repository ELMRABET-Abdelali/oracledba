#!/bin/bash
################################################################################
# Multi-Node Oracle Deployment Script
# Déploie automatiquement Oracle sur plusieurs nœuds + NFS
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="https://github.com/ELMRABET-Abdelali/oracledba.git"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"
ORACLE_ZIP="${ORACLE_ZIP:-/tmp/LINUX.X64_193000_db_home.zip}"

# Machines
NODE1_IP=""
NODE2_IP=""
NFS_IP=""
DB_NAME="RACDB"
SID1="RACDB1"
SID2="RACDB2"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

ssh_exec() {
    local host=$1
    shift
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@"$host" "$@"
}

scp_file() {
    local file=$1
    local host=$2
    local dest=$3
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$file" root@"$host":"$dest"
}

################################################################################
# Deployment Steps
################################################################################

install_oracledba_package() {
    local host=$1
    local name=$2
    
    print_info "Installation du package OracleDBA sur $name ($host)"
    
    ssh_exec "$host" "
        cd /root
        if [ -d oracledba ]; then
            rm -rf oracledba
        fi
        git clone $GITHUB_REPO
        cd oracledba
        sudo bash install.sh
    "
    
    print_success "Package OracleDBA installé sur $name"
}

setup_nfs_server() {
    local host=$1
    
    print_header "Configuration du serveur NFS ($host)"
    
    # Créer les dossiers d'export
    ssh_exec "$host" "
        mkdir -p /nfs/backup /nfs/shared /nfs/fra
        chmod 777 /nfs/backup /nfs/shared /nfs/fra
    "
    
    # Installer NFS
    ssh_exec "$host" "
        yum install -y nfs-utils
        systemctl enable nfs-server
        systemctl start nfs-server
        
        # Configure exports
        cat > /etc/exports << EOF
/nfs/backup ${NODE1_IP}(rw,sync,no_root_squash) ${NODE2_IP}(rw,sync,no_root_squash)
/nfs/shared ${NODE1_IP}(rw,sync,no_root_squash) ${NODE2_IP}(rw,sync,no_root_squash)
/nfs/fra ${NODE1_IP}(rw,sync,no_root_squash) ${NODE2_IP}(rw,sync,no_root_squash)
EOF
        
        exportfs -ra
        exportfs -v
    "
    
    print_success "Serveur NFS configuré"
}

setup_oracle_node() {
    local host=$1
    local node_name=$2
    local sid=$3
    
    print_header "Installation Oracle sur $node_name ($host)"
    
    # Upload Oracle ZIP si pas déjà présent
    if [ -f "$ORACLE_ZIP" ]; then
        print_info "Upload du fichier Oracle vers $node_name..."
        scp_file "$ORACLE_ZIP" "$host" "/tmp/"
    else
        print_warning "Oracle ZIP non trouvé: $ORACLE_ZIP"
        print_warning "Téléchargez-le manuellement sur $node_name:/tmp/"
        read -p "Appuyez sur Entrée quand c'est prêt..."
    fi
    
    # Precheck
    print_info "Vérification système..."
    ssh_exec "$host" "source ~/.bashrc && oradba precheck"
    
    # Installation Oracle
    print_info "Installation Oracle 19c..."
    ssh_exec "$host" "
        source ~/.bashrc
        
        # Generate response files
        oradba genrsp all --output-dir /tmp
        
        # Install Oracle (Phase 1: Binaries)
        cd /root/oracledba
        sudo bash oracledba/scripts/tp01-system-readiness.sh
        
        # Installation as oracle user
        sudo -u oracle bash oracledba/scripts/tp02-installation-binaire.sh
        
        # Create database
        sudo -u oracle bash oracledba/scripts/tp03-creation-instance.sh
    " | tee "install_${node_name}.log"
    
    # Mount NFS
    print_info "Configuration NFS client..."
    ssh_exec "$host" "
        mkdir -p /backup /fra /shared
        
        # Add to /etc/fstab
        grep -q '/nfs/backup' /etc/fstab || echo '${NFS_IP}:/nfs/backup /backup nfs defaults 0 0' >> /etc/fstab
        grep -q '/nfs/fra' /etc/fstab || echo '${NFS_IP}:/nfs/fra /fra nfs defaults 0 0' >> /etc/fstab
        grep -q '/nfs/shared' /etc/fstab || echo '${NFS_IP}:/nfs/shared /shared nfs defaults 0 0' >> /etc/fstab
        
        mount -a
        df -h | grep nfs
    "
    
    # Configure RMAN
    print_info "Configuration RMAN..."
    ssh_exec "$host" "
        source ~/.bashrc
        oradba rman setup --retention 7 --compression
    "
    
    # Test
    print_info "Tests de validation..."
    ssh_exec "$host" "
        source ~/.bashrc
        oradba test --full
    " | tee "test_${node_name}.log"
    
    print_success "Oracle installé et testé sur $node_name"
}

configure_dataguard() {
    print_header "Configuration Data Guard"
    
    print_info "Configuration de la réplication Primary → Standby"
    print_info "Primary: $NODE1_IP ($SID1)"
    print_info "Standby: $NODE2_IP ($SID2)"
    
    # TODO: Implémenter la configuration Data Guard automatique
    print_warning "Data Guard doit être configuré manuellement pour l'instant"
    print_info "Utilisez: oradba dataguard setup --primary $NODE1_IP --standby $NODE2_IP"
}

run_backup_test() {
    print_header "Test de backup RMAN"
    
    # Backup sur Node 1
    print_info "Backup depuis Node 1..."
    ssh_exec "$NODE1_IP" "
        source ~/.bashrc
        oradba rman backup --type full --tag NODE1_FULL_\$(date +%Y%m%d)
    "
    
    # Backup sur Node 2
    print_info "Backup depuis Node 2..."
    ssh_exec "$NODE2_IP" "
        source ~/.bashrc
        oradba rman backup --type full --tag NODE2_FULL_\$(date +%Y%m%d)
    "
    
    # Vérifier sur NFS
    print_info "Vérification des backups sur NFS..."
    ssh_exec "$NFS_IP" "ls -lh /nfs/backup/"
    
    print_success "Tests de backup réussis"
}

generate_summary() {
    print_header "Résumé du déploiement"
    
    echo -e "${GREEN}✓ Déploiement terminé!${NC}\n"
    
    echo "Architecture déployée:"
    echo "  • Node 1 (Primary): $NODE1_IP - SID: $SID1"
    echo "  • Node 2 (Standby): $NODE2_IP - SID: $SID2"
    echo "  • NFS Server: $NFS_IP"
    echo ""
    echo "Fonctionnalités activées:"
    echo "  ✓ Oracle 19c sur 2 nœuds"
    echo "  ✓ NFS centralisé pour backups"
    echo "  ✓ RMAN configuré"
    echo "  ✓ Tests automatiques"
    echo ""
    echo "Connexions:"
    echo "  Node 1: sqlplus system/password@$NODE1_IP:1521/$SID1"
    echo "  Node 2: sqlplus system/password@$NODE2_IP:1521/$SID2"
    echo ""
    echo "Logs sauvegardés:"
    echo "  • install_Node1.log"
    echo "  • install_Node2.log"
    echo "  • test_Node1.log"
    echo "  • test_Node2.log"
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "Multi-Node Oracle Deployment"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --node1)
                NODE1_IP="$2"
                shift 2
                ;;
            --node2)
                NODE2_IP="$2"
                shift 2
                ;;
            --nfs)
                NFS_IP="$2"
                shift 2
                ;;
            --db-name)
                DB_NAME="$2"
                SID1="${DB_NAME}1"
                SID2="${DB_NAME}2"
                shift 2
                ;;
            --oracle-zip)
                ORACLE_ZIP="$2"
                shift 2
                ;;
            --ssh-key)
                SSH_KEY="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Validate
    if [ -z "$NODE1_IP" ] || [ -z "$NODE2_IP" ] || [ -z "$NFS_IP" ]; then
        echo "Usage: $0 --node1 IP --node2 IP --nfs IP [--db-name NAME] [--oracle-zip PATH]"
        echo ""
        echo "Example:"
        echo "  $0 --node1 178.128.10.67 --node2 178.128.10.68 --nfs 178.128.10.69 --db-name PRODDB"
        exit 1
    fi
    
    echo "Configuration:"
    echo "  Node 1: $NODE1_IP"
    echo "  Node 2: $NODE2_IP"
    echo "  NFS: $NFS_IP"
    echo "  DB Name: $DB_NAME"
    echo "  Oracle ZIP: $ORACLE_ZIP"
    echo ""
    read -p "Continuer? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    
    # Deployment sequence
    START_TIME=$(date +%s)
    
    # Phase 1: Install OracleDBA package on all nodes
    install_oracledba_package "$NFS_IP" "NFS Server"
    install_oracledba_package "$NODE1_IP" "Node 1"
    install_oracledba_package "$NODE2_IP" "Node 2"
    
    # Phase 2: Setup NFS server
    setup_nfs_server "$NFS_IP"
    
    # Phase 3: Install Oracle on nodes
    setup_oracle_node "$NODE1_IP" "Node1" "$SID1"
    setup_oracle_node "$NODE2_IP" "Node2" "$SID2"
    
    # Phase 4: Configure Data Guard (optional)
    # configure_dataguard
    
    # Phase 5: Test backups
    run_backup_test
    
    # Summary
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    generate_summary
    echo -e "\n${GREEN}Temps total: $((DURATION / 60)) minutes $((DURATION % 60)) secondes${NC}\n"
}

main "$@"
