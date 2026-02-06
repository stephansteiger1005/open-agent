# MCP Viewing - Docker Deployment Guide

Vollständiger Leitfaden für die Bereitstellung von MCP Viewing mit Docker und Docker Compose.

## Inhaltsverzeichnis

- [Überblick](#überblick)
- [Voraussetzungen](#voraussetzungen)
- [Schnellstart](#schnellstart)
- [Architektur](#architektur)
- [Konfiguration](#konfiguration)
- [Deployment-Optionen](#deployment-optionen)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Monitoring und Logs](#monitoring-und-logs)
- [Troubleshooting](#troubleshooting)
- [Sicherheit](#sicherheit)
- [Performance-Tuning](#performance-tuning)

## Überblick

MCP Viewing läuft in einem Docker-Container und stellt **zwei parallele Services** bereit:

- **REST-API** auf Port 8080 - HTTP API für PLMXML-Datenverwaltung
- **MCP-Server** auf Port 9000 - Socket-basierter Server für Claude Desktop Integration

Beide Services laufen gleichzeitig im selben Container und teilen sich die Derby-Datenbank.

## Voraussetzungen

### Software-Anforderungen

- **Docker** 20.10 oder höher
- **Docker Compose** 2.0 oder höher (optional, aber empfohlen)
- Mindestens **2 GB RAM** für den Container
- Mindestens **1 GB freier Festplattenspeicher**

### Installation prüfen

```bash
# Docker Version prüfen
docker --version

# Docker Compose Version prüfen
docker-compose --version
```

## Schnellstart

### Mit Docker Compose (empfohlen)

```bash
# Repository klonen
git clone https://github.com/iau4u/MCP_Viewing.git
cd MCP_Viewing

# Container bauen und starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Status prüfen
docker-compose ps
```

Die Services sind nun verfügbar:
- REST-API: http://localhost:8080
- MCP-Server: localhost:9000 (Socket-Verbindung)
- Swagger UI: http://localhost:8080/swagger-ui.html
- Health Check: http://localhost:8080/actuator/health

### Mit Docker CLI

```bash
# Image bauen
docker build -t mcp-viewing:latest .

# Container starten
docker run -d \
  --name mcp-viewing \
  -p 8080:8080 \
  -p 9000:9000 \
  -e MCP_SERVER_ENABLED=true \
  -e MCP_SERVER_PORT=9000 \
  -e MCP_SERVER_MODE=socket \
  --restart unless-stopped \
  mcp-viewing:latest

# Logs anzeigen
docker logs -f mcp-viewing
```

## Architektur

### Container-Architektur

```
┌─────────────────────────────────────────────────────┐
│              Docker Container                       │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │     Spring Boot Application                  │ │
│  │                                              │ │
│  │  ┌────────────────┐  ┌──────────────────┐  │ │
│  │  │   REST API     │  │   MCP Server     │  │ │
│  │  │   Port 8080    │  │   Port 9000      │  │ │
│  │  │                │  │                  │  │ │
│  │  │  - GET/POST/   │  │  - Socket Mode   │  │ │
│  │  │    PUT/DELETE  │  │  - Multi-client  │  │ │
│  │  │  - Swagger UI  │  │  - Thread-safe   │  │ │
│  │  └────────────────┘  └──────────────────┘  │ │
│  │           │                    │            │ │
│  │           └────────┬───────────┘            │ │
│  │                    │                        │ │
│  │          ┌─────────▼──────────┐            │ │
│  │          │   PartInfoService  │            │ │
│  │          └─────────┬──────────┘            │ │
│  │                    │                        │ │
│  │          ┌─────────▼──────────┐            │ │
│  │          │  Derby Database    │            │ │
│  │          │  (In-Memory/File)  │            │ │
│  │          └────────────────────┘            │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  Exposed Ports: 8080, 9000                        │
└─────────────────────────────────────────────────────┘
         │                    │
         │                    │
    ┌────▼─────┐         ┌────▼──────┐
    │ REST     │         │  Claude   │
    │ Clients  │         │  Desktop  │
    └──────────┘         └───────────┘
```

### Prozess-Ablauf

1. **Container-Start**: Docker startet den Container mit Java und der Spring Boot Anwendung
2. **Service-Initialisierung**: 
   - REST-API wird auf Port 8080 gestartet
   - MCP-Server wird in separatem Thread auf Port 9000 gestartet
3. **Parallelbetrieb**: Beide Services laufen gleichzeitig und können unabhängig genutzt werden
4. **Datenzugriff**: Beide Services nutzen dieselbe Derby-Datenbank

## Konfiguration

### Umgebungsvariablen

#### Spring Boot Konfiguration

| Variable | Standardwert | Beschreibung |
|----------|--------------|--------------|
| `SPRING_APPLICATION_NAME` | mcp-viewing | Name der Anwendung |
| `SERVER_PORT` | 8080 | REST-API Port |
| `JAVA_OPTS` | -Xms256m -Xmx512m | JVM-Optionen |

#### Datenbank-Konfiguration

| Variable | Standardwert | Beschreibung |
|----------|--------------|--------------|
| `SPRING_DATASOURCE_URL` | jdbc:derby:memory:PARTINFODB;create=true | Derby Datenbank URL |
| `SPRING_DATASOURCE_DRIVER_CLASS_NAME` | org.apache.derby.jdbc.EmbeddedDriver | JDBC Driver |

#### MCP-Server Konfiguration

| Variable | Standardwert | Beschreibung |
|----------|--------------|--------------|
| `MCP_SERVER_ENABLED` | true | MCP-Server aktivieren/deaktivieren |
| `MCP_SERVER_PORT` | 9000 | MCP-Server Port |
| `MCP_SERVER_MODE` | socket | Modus: `socket` oder `stdio` |

#### Logging-Konfiguration

| Variable | Standardwert | Beschreibung |
|----------|--------------|--------------|
| `LOGGING_LEVEL_COM_MCPVIEWING` | DEBUG | Log-Level für MCP Viewing |
| `LOGGING_LEVEL_ROOT` | INFO | Root Log-Level |

### docker-compose.yml anpassen

```yaml
version: '3.8'

services:
  mcp-viewing:
    build:
      context: .
      dockerfile: Dockerfile
    image: mcp-viewing:latest
    container_name: mcp-viewing
    ports:
      - "8080:8080"  # REST API
      - "9000:9000"  # MCP Server
    environment:
      # Spring Boot Configuration
      - SPRING_APPLICATION_NAME=mcp-viewing
      - SERVER_PORT=8080
      
      # Database Configuration
      - SPRING_DATASOURCE_URL=jdbc:derby:memory:PARTINFODB;create=true
      - SPRING_DATASOURCE_DRIVER_CLASS_NAME=org.apache.derby.jdbc.EmbeddedDriver
      
      # MCP Server Configuration
      - MCP_SERVER_ENABLED=true
      - MCP_SERVER_PORT=9000
      - MCP_SERVER_MODE=socket
      
      # JVM Options
      - JAVA_OPTS=-Xms256m -Xmx512m
      
      # Logging
      - LOGGING_LEVEL_COM_MCPVIEWING=DEBUG
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
    
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

## Deployment-Optionen

### Option 1: In-Memory Datenbank (Standard)

Ideal für Tests und Entwicklung. Daten gehen beim Neustart verloren.

```yaml
environment:
  - SPRING_DATASOURCE_URL=jdbc:derby:memory:PARTINFODB;create=true
```

### Option 2: Persistente Datenbank mit Volume

Daten bleiben beim Neustart erhalten.

```yaml
services:
  mcp-viewing:
    # ... andere Konfiguration
    volumes:
      - ./data:/app/data
    environment:
      - SPRING_DATASOURCE_URL=jdbc:derby:/app/data/PARTINFODB;create=true
```

### Option 3: Externe Datenbank

Für Produktionsumgebungen mit separater Datenbank.

```yaml
environment:
  # Für PostgreSQL
  - SPRING_DATASOURCE_URL=jdbc:postgresql://db-host:5432/partinfodb
  - SPRING_DATASOURCE_USERNAME=user
  - SPRING_DATASOURCE_PASSWORD=password
  - SPRING_DATASOURCE_DRIVER_CLASS_NAME=org.postgresql.Driver
```

### Option 4: Multi-Container Setup

REST-API und MCP-Server in separaten Containern (fortgeschritten).

```yaml
version: '3.8'

services:
  mcp-viewing-api:
    # REST-API Container
    environment:
      - MCP_SERVER_ENABLED=false
    ports:
      - "8080:8080"
  
  mcp-viewing-server:
    # MCP-Server Container
    environment:
      - MCP_SERVER_ENABLED=true
      - MCP_SERVER_MODE=socket
      - SPRING_MAIN_WEB_APPLICATION_TYPE=none
    ports:
      - "9000:9000"
```

## Claude Desktop Integration

### Schritt 1: Container prüfen

```bash
# Container-Status prüfen
docker ps | grep mcp-viewing

# Ports prüfen
docker port mcp-viewing

# MCP-Server Logs prüfen
docker logs mcp-viewing | grep "MCP Server"
```

### Schritt 2: Socket-Verbindung testen

```bash
# Mit netcat testen
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000

# Erwartete Antwort:
# {"jsonrpc":"2.0","result":{"status":"ok"},"id":1}
```

### Schritt 3: Claude Desktop konfigurieren

Erstellen oder bearbeiten Sie `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-viewing": {
      "command": "nc",
      "args": ["localhost", "9000"]
    }
  }
}
```

**Windows PowerShell Alternative:**

```json
{
  "mcpServers": {
    "mcp-viewing": {
      "command": "powershell",
      "args": [
        "-Command",
        "$client = New-Object System.Net.Sockets.TcpClient('localhost', 9000); $stream = $client.GetStream(); $reader = New-Object System.IO.StreamReader($stream); $writer = New-Object System.IO.StreamWriter($stream); $writer.AutoFlush = $true; while ($true) { $line = [Console]::ReadLine(); if ($line) { $writer.WriteLine($line); $response = $reader.ReadLine(); [Console]::WriteLine($response) } }"
      ]
    }
  }
}
```

### Schritt 4: Claude Desktop neu starten

1. Claude Desktop vollständig beenden
2. Claude Desktop neu starten
3. Im Chat nach verfügbaren Tools fragen: "Welche Tools hast du zur Verfügung?"

### Verfügbare MCP-Tools

1. **get_partinfo_latest** - Neueste PLMXML-Daten abrufen
2. **get_partinfo_specific** - Spezifische Version abrufen
3. **create_partinfo** - PLMXML-Daten erstellen/aktualisieren
4. **delete_partinfo** - PLMXML-Daten löschen

## Monitoring und Logs

### Schnelle Status-Überprüfung

Das Projekt enthält ein dediziertes Script zur umfassenden Überprüfung des Container-Status:

```bash
./check-docker-status.sh
```

**Das Script überprüft automatisch:**

1. ✓ Docker-Installation und -Daemon-Status
2. ✓ Container-Existenz und aktueller Zustand
3. ✓ Port-Mappings (8080, 9000)
4. ✓ Health Check Status
5. ✓ Ressourcennutzung (CPU, Memory, I/O)
6. ✓ REST-API Konnektivität
7. ✓ MCP-Server Konnektivität
8. ✓ Aktuelle Container-Logs
9. ✓ Umgebungsvariablen
10. ✓ Zusammenfassung und Empfehlungen

**Beispiel-Ausgabe bei laufendem Container:**

```
============================================
MCP_Viewing - Docker Container Status Check
============================================

1. Checking Docker availability...
✓ Docker is installed and running

2. Checking if container 'mcp-viewing' exists...
✓ Container 'mcp-viewing' exists

3. Container Status:
   Status: running
   Running: true
   Started at: 2026-01-23T15:30:00.000Z
✓ Container is running

4. Port Mappings:
ℹ 8080/tcp -> 0.0.0.0:8080
ℹ 9000/tcp -> 0.0.0.0:9000

5. Health Check Status:
✓ Container is healthy

6. Resource Usage:
   CPU %      Memory Usage       Memory %   Network I/O
   2.45%      256MiB / 512MiB    50%        1.2MB / 500kB
✓ Resource usage retrieved successfully

7. Testing REST API (Port 8080):
✓ REST API is responding (HTTP 200)
✓ Application health status: UP

8. Testing MCP Server (Port 9000):
✓ MCP Server port 9000 is listening
✓ MCP Server is responding to JSON-RPC requests

...

============================================
Summary
============================================

✓ Container is running and healthy

Available endpoints:
  • REST API: http://localhost:8080
  • Swagger UI: http://localhost:8080/swagger-ui.html
  • Health Check: http://localhost:8080/actuator/health
  • MCP Server: localhost:9000 (Socket connection)
```

### Container-Status (Manuelle Befehle)

```bash
# Container-Status
docker-compose ps

# Ressourcennutzung
docker stats mcp-viewing

# Health Check
curl http://localhost:8080/actuator/health
```

### Logs anzeigen

```bash
# Alle Logs
docker-compose logs

# Logs verfolgen
docker-compose logs -f

# Nur MCP-Server Logs
docker-compose logs | grep "MCP Server"

# Nur Fehler
docker-compose logs | grep ERROR

# Letzte 100 Zeilen
docker-compose logs --tail=100
```

### Health Checks

```bash
# REST-API Health Check
curl http://localhost:8080/actuator/health

# MCP-Server Ping
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000

# Docker Health Status
docker inspect --format='{{.State.Health.Status}}' mcp-viewing
```

## Troubleshooting

### Generelle Problemdiagnose

**Erste Schritte bei Problemen:**

1. Führen Sie das Status-Check-Script aus:
   ```bash
   ./check-docker-status.sh
   ```
   
   Dieses Script diagnostiziert automatisch häufige Probleme und gibt spezifische Empfehlungen.

2. Prüfen Sie die Container-Logs:
   ```bash
   docker-compose logs -f
   ```

3. Falls das Problem weiterhin besteht, siehe spezifische Problemlösungen unten:

### Problem: Container startet nicht

**Symptome:**
```bash
docker-compose ps
# zeigt: Exit 1 oder Restarting
```

**Lösungen:**

```bash
# 1. Logs prüfen
docker-compose logs

# 2. Port-Konflikte prüfen
netstat -tuln | grep -E '8080|9000'

# 3. Container neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. Java-Fehler prüfen
docker-compose logs | grep -i "exception\|error"
```

### Problem: MCP-Server nicht erreichbar

**Symptome:**
```bash
nc localhost 9000
# Verbindung fehlgeschlagen
```

**Lösungen:**

```bash
# 1. MCP-Server aktiviert?
docker exec mcp-viewing env | grep MCP_SERVER_ENABLED

# 2. Port-Mapping prüfen
docker port mcp-viewing 9000

# 3. Firewall prüfen
sudo ufw status | grep 9000

# 4. MCP-Server Logs
docker logs mcp-viewing | grep "MCP Server"
```

### Problem: REST-API antwortet nicht

**Symptome:**
```bash
curl http://localhost:8080/actuator/health
# Keine Antwort
```

**Lösungen:**

```bash
# 1. Container läuft?
docker ps | grep mcp-viewing

# 2. Port 8080 frei?
netstat -tuln | grep 8080

# 3. Spring Boot gestartet?
docker logs mcp-viewing | grep "Started McpViewingApplication"

# 4. Health Check Status
docker inspect mcp-viewing | grep -A 10 Health
```

### Problem: Datenbank-Fehler

**Symptome:**
```
java.sql.SQLException: Failed to create database
```

**Lösungen:**

```bash
# 1. Volume-Berechtigungen prüfen (bei persistenter DB)
ls -la ./data
chmod -R 755 ./data

# 2. In-Memory DB verwenden
docker-compose down
# docker-compose.yml anpassen:
# SPRING_DATASOURCE_URL=jdbc:derby:memory:PARTINFODB;create=true
docker-compose up -d

# 3. Datenbank neu erstellen
rm -rf ./data
docker-compose up -d
```

### Problem: Hohe CPU/RAM-Nutzung

**Lösungen:**

```bash
# 1. Ressourcen prüfen
docker stats mcp-viewing

# 2. JVM-Optionen anpassen in docker-compose.yml:
environment:
  - JAVA_OPTS=-Xms128m -Xmx256m

# 3. Container neu starten
docker-compose restart

# 4. Log-Level reduzieren
environment:
  - LOGGING_LEVEL_COM_MCPVIEWING=INFO
```

### Problem: Claude Desktop verbindet nicht

**Lösungen:**

```bash
# 1. Socket-Verbindung testen
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000

# 2. Claude Desktop Logs prüfen
# macOS: ~/Library/Logs/Claude/mcp.log
# Windows: %APPDATA%\Claude\logs\mcp.log

# 3. Konfiguration validieren
cat ~/.config/Claude/claude_desktop_config.json | jq .

# 4. nc installiert?
which nc
# Falls nicht: sudo apt install netcat (Linux) / brew install netcat (macOS)
```

## Sicherheit

### Best Practices

1. **Netzwerk-Isolation**
   ```yaml
   networks:
     mcp-network:
       driver: bridge
       internal: true  # Kein Internet-Zugang
   ```

2. **Read-Only Container**
   ```yaml
   services:
     mcp-viewing:
       read_only: true
       tmpfs:
         - /tmp
   ```

3. **Resource Limits**
   ```yaml
   services:
     mcp-viewing:
       deploy:
         resources:
           limits:
             cpus: '1.0'
             memory: 512M
           reservations:
             cpus: '0.5'
             memory: 256M
   ```

4. **Secrets Management**
   ```yaml
   services:
     mcp-viewing:
       secrets:
         - db_password
   
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

### Nur localhost-Zugriff

```yaml
ports:
  - "127.0.0.1:8080:8080"
  - "127.0.0.1:9000:9000"
```

## Performance-Tuning

### JVM-Optimierung

```yaml
environment:
  - JAVA_OPTS=-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

### Thread Pool anpassen

Für viele gleichzeitige MCP-Verbindungen:

```yaml
environment:
  - SERVER_TOMCAT_THREADS_MAX=200
  - SERVER_TOMCAT_THREADS_MIN_SPARE=10
```

### Datenbank-Tuning

```yaml
environment:
  - SPRING_JPA_PROPERTIES_HIBERNATE_JDBC_BATCH_SIZE=20
  - SPRING_JPA_PROPERTIES_HIBERNATE_ORDER_INSERTS=true
  - SPRING_JPA_PROPERTIES_HIBERNATE_ORDER_UPDATES=true
```

## Wartung

### Regelmäßige Aufgaben

```bash
# Container-Logs rotieren (wöchentlich)
docker-compose logs > logs-$(date +%Y%m%d).txt
docker-compose restart

# Image aktualisieren (monatlich)
docker-compose pull
docker-compose up -d

# Ungenutzte Images löschen
docker image prune -a

# Volumes aufräumen
docker volume prune
```

### Backup

```bash
# Datenbank-Backup (bei persistenter DB)
docker exec mcp-viewing tar czf /tmp/backup.tar.gz /app/data
docker cp mcp-viewing:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# Konfiguration sichern
tar czf config-backup.tar.gz docker-compose.yml .env
```

### Updates

```bash
# 1. Backup erstellen
docker-compose down
tar czf backup-$(date +%Y%m%d).tar.gz data/

# 2. Neue Version bauen
git pull
docker-compose build --no-cache

# 3. Starten und testen
docker-compose up -d
docker-compose logs -f

# 4. Health Check
curl http://localhost:8080/actuator/health
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000
```

## Weitere Ressourcen

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Spring Boot Docker Guide](https://spring.io/guides/gs/spring-boot-docker/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Projekt Repository](https://github.com/iau4u/MCP_Viewing)
