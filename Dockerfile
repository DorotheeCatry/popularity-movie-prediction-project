# 1. Utiliser une image Python officielle légère
ARG PYTHON_VERSION=3.11.8
FROM python:${PYTHON_VERSION}-slim AS base

# 2. Variables d'environnement utiles
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Définir le répertoire de travail
WORKDIR /app

# 4. Mise à jour et installation des bibliothèques système requises
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    chromium \
    chromium-driver \
    libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 5. Variables d'environnement Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/lib/chromium/chromedriver

# 6. Créer un utilisateur non-root sécurisé
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# 7. Installer les dépendances Python
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# 8. Ajouter le chemin des binaires Python au PATH
ENV PATH="/usr/local/bin:${PATH}"

# 9. Passer à l'utilisateur non-root
USER appuser

# 10. Copier le reste du code de l'application
COPY . /app/

# 11. Exposer le port
EXPOSE 8000

# 12. Lancer le serveur Django via Gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]