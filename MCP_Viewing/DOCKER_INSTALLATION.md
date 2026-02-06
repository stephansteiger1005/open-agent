# MCP Viewing - Docker Installation

Diese Anleitung beschreibt die Installation und Nutzung von MCP Viewing über Docker.

## Voraussetzungen

- Docker installiert und lauffähig
- Docker Compose (optional, aber empfohlen)
- Mindestens 4 GB RAM verfügbar
- Internetverbindung für den initialen Download des Docker-Images
- **Zugriffstoken** (wird Ihnen vom Administrator bereitgestellt oder siehe [TOKEN_CREATION.md](TOKEN_CREATION.md) für Anleitung zur Erstellung)

## Authentifizierung mit GitHub Container Registry

Da das Docker-Image in einem privaten Repository gespeichert ist, müssen Sie sich zunächst mit dem bereitgestellten Zugriffstoken authentifizieren.

### Schritt 1: Token-Datei vorbereiten

Speichern Sie das bereitgestellte Zugriffstoken in einer Datei oder kopieren Sie es in die Zwischenablage.

### Schritt 2: Bei GitHub Container Registry anmelden

Führen Sie folgenden Befehl aus und geben Sie das Token ein, wenn Sie dazu aufgefordert werden:

```bash
echo "IHR_ZUGRIFFSTOKEN" | docker login ghcr.io -u USERNAME --password-stdin
```

**Ersetzen Sie:**
- `IHR_ZUGRIFFSTOKEN` durch das Ihnen bereitgestellte Token
- `USERNAME` durch Ihren GitHub-Benutzernamen (oder den vom Administrator angegebenen Benutzernamen)

**Beispiel:**
```bash
echo "ghp_xxxxxxxxxxxxxxxxxxxx" | docker login ghcr.io -u iau4u --password-stdin
```

Nach erfolgreicher Anmeldung sehen Sie: `Login Succeeded`

**Hinweis:** Das Zugriffstoken berechtigt Sie **ausschließlich** zum Herunterladen des Docker-Containers. Ein Zugriff auf den Quellcode oder andere Repository-Inhalte ist damit nicht möglich.

## Installation

### Option 1: Mit Docker Compose (empfohlen)

1. Erstellen Sie eine `docker-compose.yml` Datei:

```yaml
version: '3.8'

services:
  mcp-viewing:
    image: ghcr.io/iau4u/mcp-viewing:latest
    container_name: mcp-viewing
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - NODE_ENV=production
    restart: unless-stopped
```

2. Starten Sie den Container:

```bash
docker-compose up -d
```

### Option 2: Mit Docker CLI

```bash
docker run -d \
  --name mcp-viewing \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -e NODE_ENV=production \
  --restart unless-stopped \
  ghcr.io/iau4u/mcp-viewing:latest
```

## Zugriff auf die Anwendung

Nach dem Start ist die Anwendung unter folgender URL erreichbar:

```
http://localhost:8080
```

## Container-Verwaltung

### Container stoppen

```bash
docker-compose down
```

oder

```bash
docker stop mcp-viewing
```

### Container neu starten

```bash
docker-compose restart
```

oder

```bash
docker restart mcp-viewing
```

### Logs anzeigen

```bash
docker-compose logs -f
```

oder

```bash
docker logs -f mcp-viewing
```

## Konfiguration

Die Konfigurationsdateien befinden sich im `config`-Verzeichnis. Nach Änderungen muss der Container neu gestartet werden.

## Daten-Persistenz

Die Daten werden im `data`-Verzeichnis gespeichert und bleiben auch nach dem Neustart des Containers erhalten.

## Updates

Um auf eine neue Version zu aktualisieren:

```bash
docker-compose pull
docker-compose up -d
```

oder

```bash
docker pull ghcr.io/iau4u/mcp-viewing:latest
docker stop mcp-viewing
docker rm mcp-viewing
# Container mit neuem Image starten (siehe Installation)
```

## Fehlerbehebung

### Authentifizierungsfehler beim Herunterladen

**Symptom:** Fehlermeldung wie "unauthorized: authentication required" oder "denied: requested access to the resource is denied"

**Lösung:** 
1. Überprüfen Sie, ob Sie mit dem korrekten Token angemeldet sind
2. Melden Sie sich erneut an (siehe Abschnitt "Authentifizierung")
3. Stellen Sie sicher, dass das Token noch gültig ist

### Port bereits belegt

Falls Port 8080 bereits verwendet wird, ändern Sie in der `docker-compose.yml` oder im `docker run`-Befehl den ersten Port (z.B. `8081:8080`).

### Container startet nicht

Überprüfen Sie die Logs:

```bash
docker logs mcp-viewing
```

### Berechtigungsprobleme

Stellen Sie sicher, dass die gemounteten Verzeichnisse die richtigen Berechtigungen haben:

```bash
chmod -R 755 data config
```

## Lizenz

Diese Software ist ausschließlich für die Nutzung durch Daimler Buses lizenziert und unterliegt einer geschlossenen, proprietären Lizenz.

**Ansprechpartner:**  
Hans-Georg Höhne  
E-Mail: hans-georg.hoehne@daimlertruck.com

---

**Hinweis zur Sicherheit:** Geben Sie Ihr Zugriffstoken niemals an Dritte weiter und speichern Sie es an einem sicheren Ort.

**Weitere Informationen zur Token-Erstellung:** Eine ausführliche Anleitung zur Erstellung verschiedener Zugriffstoken-Typen finden Sie in [TOKEN_CREATION.md](TOKEN_CREATION.md).