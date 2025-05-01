#!/bin/bash

# Variables
RESOURCE_GROUP="dcatryRG"
CONTAINER_NAME="fastapi-app"
ACR_NAME="dcatryregistry"
ACR_IMAGE="fastapi-app"
ACR_URL="$ACR_NAME.azurecr.io"
CPU="1"
MEMORY="4"
PORT="8001"
IP_ADDRESS="Public"
DNS_LABEL="api-loanrequest"  # ⚠ Azure DNS n'accepte que des lettres minuscules !
OS_TYPE="Linux"

# Vérification et chargement des variables d'environnement
if [ -f .env ]; then
    echo "✅ .env file found. Loading environment variables..."
    set -o allexport
    source .env
    set +o allexport
else
    echo "❌ .env file not found!"
    exit 1
fi

# Récupération des identifiants ACR
echo "🔑 Retrieving ACR credentials..."
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

# Vérification de l'existence du conteneur et suppression s'il existe
EXISTING_CONTAINER=$(az container show --name "$CONTAINER_NAME" --resource-group "$RESOURCE_GROUP" --query "name" -o tsv 2>/dev/null)
if [ "$EXISTING_CONTAINER" == "$CONTAINER_NAME" ]; then
    echo "🗑️  Deleting existing container..."
    az container delete --name "$CONTAINER_NAME" --resource-group "$RESOURCE_GROUP" --yes
fi

# Déploiement du conteneur sur Azure Container Instances
echo "🚀 Deploying container to Azure Container Instances..."
az container create \
  --name "$CONTAINER_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --image "$ACR_URL/$ACR_IMAGE" \
  --cpu "$CPU" \
  --memory "$MEMORY" \
  --registry-login-server "$ACR_URL" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --ports "$PORT" \
  --ip-address "$IP_ADDRESS" \
  --dns-name-label "$DNS_LABEL" \
  --os-type "$OS_TYPE" \
  --environment-variables SECRET_KEY="$SECRET_KEY" \
    ALGORITHM="$ALGORITHM" \
    ACCESS_TOKEN_EXPIRE_MINUTES="$ACCESS_TOKEN_EXPIRE_MINUTES" \
    PORT="$PORT" \
    DB_USERNAME="$DB_USERNAME" \
    DB_PASSWORD="$DB_PASSWORD" \
    DB_SERVER="$DB_SERVER" \
    DB_NAME="$DB_NAME" \
    DB_DRIVER="$DB_DRIVER" \
    DATABASE_URL="$DATABASE_URL"

# Vérification du succès du déploiement
if [ $? -eq 0 ]; then
    # Récupération de la région de l'application
    LOCATION=$(az container show --name "$CONTAINER_NAME" --resource-group "$RESOURCE_GROUP" --query "location" -o tsv)
    echo "✅ Deployment succeeded!"
    echo "🌍 Container URL: http://$DNS_LABEL.$LOCATION.azurecontainer.io:$PORT"
else
    echo "❌ Deployment failed!"
    exit 1
fi
