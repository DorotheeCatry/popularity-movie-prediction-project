#!/bin/bash

# Nom du spider
SPIDER_NAME="allocinespider"

# Dossier JOBDIR
JOBDIR_PATH="crawls/$SPIDER_NAME"

# Vérification si le dossier JOBDIR existe
if [ -d "$JOBDIR_PATH" ]; then
    echo "🔄 Jobdir found. Resuming previous crawl from $JOBDIR_PATH."
else
    echo "🆕 No existing jobdir found. Starting a new crawl."
fi

# Lancement du spider avec niveau de log en INFO pour mieux suivre
scrapy crawl "$SPIDER_NAME" -s LOG_LEVEL=INFO
