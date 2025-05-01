#!/bin/bash

# Arrêt immédiat si une commande échoue
set -e

echo "🚀 Mise à jour des paquets et installation des dépendances requises..."
apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Ajouter la clé Microsoft et le dépôt
echo "🔑 Ajout du dépôt Microsoft..."
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Mettre à jour la liste des paquets
apt-get update

# Accepter la licence EULA et installer le driver ODBC
echo "📦 Installation du driver ODBC msodbcsql18..."
ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get install -y msodbcsql18 unixodbc

# Installation des outils SQL (optionnel mais recommandé)
ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get install -y mssql-tools18

# Ajouter mssql-tools au PATH
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> /etc/profile.d/mssql-tools.sh

# Vérifier que l'installation s'est bien déroulée
echo "🔍 Vérification des drivers installés..."
odbcinst -q -d

echo "✅ Installation terminée avec succès !"