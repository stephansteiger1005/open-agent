# MCP Integration Guide

## Überblick

Das **Model Context Protocol (MCP)** ist ein offener Standard von Anthropic, der es KI-Modellen (insbesondere Claude) ermöglicht, mit externen Systemen, APIs und Datenquellen zu interagieren.

MCP Viewing implementiert einen vollständigen MCP-Server, der **parallel zur REST-API** läuft:

- **REST-API** auf Port 8080 - HTTP API für PLMXML-Datenverwaltung
- **MCP-Server (HTTP)** auf http://localhost:8080/mcp - HTTP/SSE Transport für OpenAI Proxy und Web-basierte Clients
- **MCP-Server (Socket)** auf Port 9000 - Socket-basierter Server für Claude Desktop

## Installation und Setup

### 🐳 Empfohlene Methode: Docker (schnellste Installation)

Docker ist die **empfohlene Installationsmethode**, da beide Services (REST-API und MCP-Server) automatisch parallel gestartet werden.

#### Voraussetzungen

- Docker 20.10+
- Docker Compose 2.0+
- Claude Desktop

#### Schnellstart

```bash
# Repository klonen
git clone https://github.com/iau4u/MCP_Viewing.git
cd MCP_Viewing

# Mit Docker Compose starten
docker-compose up -d

# Status prüfen
docker-compose ps
docker-compose logs -f
```

Die Services sind nun verfügbar:
- **REST-API**: http://localhost:8080
- **MCP-Server (HTTP)**: http://localhost:8080/mcp - für OpenAI Proxy und Web-Clients
- **MCP-Server (Socket)**: localhost:9000 - für Claude Desktop
- **Swagger UI**: http://localhost:8080/swagger-ui.html

#### MCP-Server testen

**Socket-Transport testen:**
```bash
# Socket-Verbindung testen
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000

# Erwartete Antwort:
# {"jsonrpc":"2.0","result":{"status":"ok"},"id":1}
```

**HTTP-Transport testen:**
```bash
# HTTP POST Anfrage
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'

# Erwartete Antwort:
# {"jsonrpc":"2.0","result":{"status":"ok"},"id":1.0}

# Health Check
curl http://localhost:8080/mcp/health

# MCP Initialize
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"0.1.0","clientInfo":{"name":"test","version":"1.0"}},"id":1}'

# Tools auflisten
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'
```

### Alternative: Manuelle Installation

Wenn Sie Docker nicht verwenden möchten:

```bash
# JAR-Datei bauen
mvn clean package -DskipTests

# Beide Services parallel starten
java -jar target/mcp-viewing-1.0.0.jar \
  --mcp.server.enabled=true \
  --mcp.server.mode=socket \
  --mcp.server.port=9000
```

**Hinweis:** Im manuellen Modus laufen beide Services im selben Prozess. Der MCP-Server läuft in einem separaten Thread und blockiert die REST-API nicht.

## Claude Desktop Integration

### Schritt 1: Container vorbereiten (Docker-Methode)

```bash
# Sicherstellen, dass der Container läuft
docker ps | grep mcp-viewing

# MCP-Server Logs prüfen
docker logs mcp-viewing | grep "MCP Server listening"

# Sollte zeigen:
# MCP Server listening on port 9000
```

### Schritt 2: Claude Desktop konfigurieren

#### macOS/Linux

Erstellen oder bearbeiten Sie: `~/.config/Claude/claude_desktop_config.json`

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

**Wichtig:** `nc` (netcat) muss installiert sein:

```bash
# macOS
brew install netcat

# Ubuntu/Debian
sudo apt install netcat

# Fedora/RHEL
sudo dnf install nc
```

#### Windows

Erstellen oder bearbeiten Sie: `%APPDATA%\Claude\claude_desktop_config.json`

**Option 1: Mit netcat (empfohlen)**

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

Netcat für Windows: https://eternallybored.org/misc/netcat/

**Option 2: Mit PowerShell**

```json
{
  "mcpServers": {
    "mcp-viewing": {
      "command": "powershell",
      "args": [
        "-NoProfile",
        "-Command",
        "$client = New-Object System.Net.Sockets.TcpClient('localhost', 9000); $stream = $client.GetStream(); $reader = New-Object System.IO.StreamReader($stream); $writer = New-Object System.IO.StreamWriter($stream); $writer.AutoFlush = $true; while ($true) { $line = [Console]::ReadLine(); if ($line) { $writer.WriteLine($line); $response = $reader.ReadLine(); [Console]::WriteLine($response) } }"
      ]
    }
  }
}
```

### Schritt 3: Claude Desktop neu starten

1. Claude Desktop vollständig beenden
2. Claude Desktop neu starten
3. Im Chat testen: "Welche Tools hast du zur Verfügung?"

Claude sollte die 4 MCP-Tools anzeigen.

## OpenAI Proxy / OpenWebUI Integration

Der MCP-Server unterstützt jetzt den **Streamable HTTP Transport**, der von OpenAI Proxy und OpenWebUI verwendet wird.

### Konfiguration für OpenAI Proxy

Der OpenAI Proxy verbindet sich automatisch über HTTP zum MCP-Server:

1. **MCP-Server starten** (mit Docker oder manuell wie oben beschrieben)

2. **OpenAI Proxy konfigurieren:**
```yaml
# OpenAI Proxy Konfiguration (docker-compose.yml oder .env)
MCP_SERVERS:
  mcp-viewing:
    url: "http://mcp-viewing:8080/mcp"
    transport: "http"
```

Oder wenn der MCP-Server auf einem anderen Host läuft:
```yaml
MCP_SERVERS:
  mcp-viewing:
    url: "http://localhost:8080/mcp"
    transport: "http"
```

3. **Verbindung testen:**
```bash
# Vom OpenAI Proxy Container aus:
curl -X POST http://mcp-viewing:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"0.1.0","clientInfo":{"name":"openai-proxy","version":"1.0"}},"id":1}'
```

### Verfügbare Transports

Der MCP-Server unterstützt jetzt alle gängigen Transports:

| Transport | Endpunkt | Verwendung |
|-----------|----------|------------|
| **HTTP** | `http://localhost:8080/mcp` | OpenAI Proxy, OpenWebUI, Web-Clients |
| **SSE** | `http://localhost:8080/mcp` (GET) | Streaming für lange Verbindungen |
| **Socket** | `localhost:9000` | Claude Desktop (via netcat) |
| **Stdio** | stdin/stdout | Direkte Prozess-Integration |

### CORS-Unterstützung

Der HTTP-Transport unterstützt CORS (Cross-Origin Resource Sharing) für Web-basierte Clients:

- **Allowed Origins:** `*` (kann in Produktion eingeschränkt werden)
- **Allowed Methods:** `GET, POST, OPTIONS`
- **Allowed Headers:** `Content-Type, Authorization, X-Requested-With, Accept, Origin`
- **Max Age:** 3600 Sekunden

## Verfügbare MCP-Tools

### 1. get_partinfo_latest

**Beschreibung:** Ruft die neuesten PLMXML-Daten für eine gegebene Sachnummer ab.

**Parameter:**
- `sachnummer` (string, erforderlich): Die Teilenummer

**Beispiel:**
```
Claude: Hole die neuesten Daten für Teil PART-12345
```

**JSON-RPC Aufruf:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_partinfo_latest",
    "arguments": {
      "sachnummer": "PART-12345"
    }
  },
  "id": 1
}
```

### 2. get_partinfo_specific

**Beschreibung:** Ruft eine spezifische PLMXML-Version ab.

**Parameter:**
- `sachnummer` (string, erforderlich): Die Teilenummer
- `revision` (integer, erforderlich): Revisionsnummer
- `sequenz` (integer, erforderlich): Sequenznummer

**Beispiel:**
```
Claude: Zeige mir PART-12345, Revision 2, Sequenz 1
```

### 3. create_partinfo

**Beschreibung:** Erstellt oder aktualisiert PLMXML-Teile-Informationen.

**Parameter:**
- `sachnummer` (string, erforderlich)
- `revision` (integer, erforderlich)
- `sequenz` (integer, erforderlich)
- `clazz` (string, erforderlich): z.B. "Part", "Assembly"
- `plmxml` (string, erforderlich): Base64-kodierter PLMXML-Inhalt
- `nomenclature` (string, optional): Beschreibung
- `owner` (string, optional)
- `status` (string, optional)

**Beispiel:**
```
Claude: Erstelle ein neues Teil mit Sachnummer PART-99999, 
Revision 1, Sequenz 1, Klasse "Part"
```

### 4. delete_partinfo

**Beschreibung:** Löscht PLMXML-Teile-Informationen.

**Parameter:**
- `sachnummer` (string, erforderlich)
- `revision` (integer, erforderlich)
- `sequenz` (integer, erforderlich)

**Beispiel:**
```
Claude: Lösche PART-12345, Revision 1, Sequenz 1
```

## Architektur

### System-Architektur

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
│  │  │  - Swagger UI  │  │  - Socket Mode   │  │ │
│  │  │  - OpenAPI     │  │  - JSON-RPC 2.0  │  │ │
│  │  │  - HTTP/REST   │  │  - Multi-Thread  │  │ │
│  │  └────────┬───────┘  └────────┬─────────┘  │ │
│  │           │                    │            │ │
│  │           └────────┬───────────┘            │ │
│  │                    │                        │ │
│  │          ┌─────────▼──────────┐            │ │
│  │          │  PartInfoService   │            │ │
│  │          │  (Business Logic)  │            │ │
│  │          └─────────┬──────────┘            │ │
│  │                    │                        │ │
│  │          ┌─────────▼──────────┐            │ │
│  │          │  Derby Database    │            │ │
│  │          │  (Shared Storage)  │            │ │
│  │          └────────────────────┘            │ │
│  └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │                    │
         │                    │
    ┌────▼─────┐         ┌────▼──────┐
    │ REST     │         │  Claude   │
    │ Clients  │         │  Desktop  │
    │ (Swagger,│         │  (via nc) │
    │  curl)   │         │           │
    └──────────┘         └───────────┘
```

### Kommunikationsablauf

1. **Claude Desktop** → **netcat** → **MCP-Server (Port 9000)**
2. **MCP-Server** → **ToolRegistry** → **PartInfoService**
3. **PartInfoService** → **Derby Database**
4. **Response** zurück über dieselbe Kette

## Betriebsmodi

Der MCP-Server unterstützt drei Modi:

### 1. HTTP-Modus (für OpenAI Proxy, Web-Clients)

**NEU:** Unterstützt jetzt Streamable HTTP Transport!

```yaml
environment:
  - MCP_SERVER_ENABLED=true
```

**Vorteile:**
- ✅ Standard HTTP/HTTPS Protokoll
- ✅ Server-Sent Events (SSE) für Streaming
- ✅ CORS-Unterstützung für Web-Clients
- ✅ Integration mit OpenAI Proxy und OpenWebUI
- ✅ Parallelbetrieb mit REST-API
- ✅ Keine zusätzlichen Ports erforderlich

**Endpunkte:**
- `POST /mcp` - JSON-RPC 2.0 Anfragen
- `GET /mcp` - Server-Sent Events (SSE) Streaming
- `GET /mcp/health` - Health Check

**Verwendung:**
```bash
# Mit OpenAI Proxy
# Der Proxy verbindet sich zu http://localhost:8080/mcp

# Oder direkt testen
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### 2. Socket-Modus (Standard, für Docker)

```yaml
environment:
  - MCP_SERVER_MODE=socket
  - MCP_SERVER_PORT=9000
```

**Vorteile:**
- ✅ Parallelbetrieb mit REST-API
- ✅ Mehrere Clients gleichzeitig möglich
- ✅ Non-blocking
- ✅ Ideal für Docker

### 3. Stdio-Modus (für direkte Integration)

```yaml
environment:
  - MCP_SERVER_MODE=stdio
```

**Vorteile:**
- ✅ Direkte Prozess-Kommunikation
- ✅ Keine Ports erforderlich
- ✅ Einfache Claude Desktop Integration

**Nachteil:**
- ❌ REST-API nicht parallel nutzbar

**Claude Desktop Konfiguration (Stdio-Modus):**

```json
{
  "mcpServers": {
    "mcp-viewing": {
      "command": "java",
      "args": [
        "-jar",
        "/absoluter/pfad/zu/mcp-viewing-1.0.0.jar",
        "--mcp.server.enabled=true",
        "--mcp.server.mode=stdio",
        "--spring.main.web-application-type=none"
      ]
    }
  }
}
```

## Konfiguration

### application.properties

```properties
# MCP Server Configuration
mcp.server.enabled=false
mcp.server.port=9000
mcp.server.mode=socket
```

### Docker Environment Variables

```yaml
environment:
  - MCP_SERVER_ENABLED=true
  - MCP_SERVER_PORT=9000
  - MCP_SERVER_MODE=socket
```

### Nur REST-API (MCP deaktivieren)

```bash
docker run -d \
  -p 8080:8080 \
  -e MCP_SERVER_ENABLED=false \
  mcp-viewing:latest
```

### Nur MCP-Server (REST deaktivieren)

```bash
docker run -d \
  -p 9000:9000 \
  -e MCP_SERVER_ENABLED=true \
  -e SPRING_MAIN_WEB_APPLICATION_TYPE=none \
  mcp-viewing:latest
```

## MCP-Protokoll Details

### Initialisierung

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "0.1.0",
    "clientInfo": {
      "name": "Claude Desktop",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "0.1.0",
    "serverInfo": {
      "name": "mcp-viewing",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {
        "supportsProgress": false
      }
    }
  },
  "id": 1
}
```

### Tools auflisten

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 2
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "get_partinfo_latest",
        "description": "Get latest PLMXML data for a part number",
        "inputSchema": { ... }
      },
      ...
    ]
  },
  "id": 2
}
```

### Tool aufrufen

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_partinfo_latest",
    "arguments": {
      "sachnummer": "PART-12345"
    }
  },
  "id": 3
}
```

## Troubleshooting

### Problem: MCP-Server startet nicht

**Symptome:**
```bash
docker logs mcp-viewing
# Zeigt keine "MCP Server listening" Nachricht
```

**Lösung:**
```bash
# 1. MCP_SERVER_ENABLED prüfen
docker exec mcp-viewing env | grep MCP_SERVER_ENABLED

# 2. Logs nach Fehlern durchsuchen
docker logs mcp-viewing | grep -i error

# 3. Container neu starten
docker-compose restart
```

### Problem: Claude Desktop verbindet nicht

**Lösung 1: Socket-Verbindung testen**
```bash
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000
```

**Lösung 2: nc verfügbar?**
```bash
which nc
# Falls nicht installiert: brew install netcat (macOS)
```

**Lösung 3: Claude Desktop Logs prüfen**
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp.log

# Windows
type %APPDATA%\Claude\logs\mcp.log
```

**Lösung 4: Port-Konflikt prüfen**
```bash
netstat -tuln | grep 9000
```

### Problem: "Tools werden nicht angezeigt"

**Lösungen:**

1. **Konfiguration validieren:**
```bash
cat ~/.config/Claude/claude_desktop_config.json | jq .
```

2. **MCP-Server ping testen:**
```bash
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | nc localhost 9000
```

3. **Claude Desktop neu starten** (vollständig beenden und neu öffnen)

### Problem: Verbindung bricht ab

**Lösung:**
```bash
# Keep-alive für lange Verbindungen
docker-compose up -d
docker logs -f mcp-viewing

# Bei häufigen Abbrüchen: Timeout erhöhen
# In docker-compose.yml:
environment:
  - SERVER_CONNECTION_TIMEOUT=300000
```

### Problem: "Port 9000 already in use"

**Lösung:**
```bash
# 1. Prozess finden
lsof -i :9000

# 2. Prozess beenden
kill -9 <PID>

# 3. Oder anderen Port verwenden
# In docker-compose.yml:
ports:
  - "9001:9000"
environment:
  - MCP_SERVER_PORT=9000
```

## Best Practices

### 1. Docker-Container Monitoring

```bash
# Container-Status überwachen
watch -n 5 'docker stats mcp-viewing --no-stream'

# Logs in Echtzeit
docker-compose logs -f --tail=50
```

### 2. Health Checks

```bash
# REST-API Health
curl http://localhost:8080/actuator/health

# MCP-Server Health
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000

# Beide parallel prüfen
curl http://localhost:8080/actuator/health && \
echo '{"jsonrpc":"2.0","method":"ping","id":1}' | nc localhost 9000
```

### 3. Logging-Konfiguration

Für Produktionsumgebungen:

```yaml
environment:
  - LOGGING_LEVEL_COM_MCPVIEWING=INFO
  - LOGGING_LEVEL_ROOT=WARN
```

Für Debugging:

```yaml
environment:
  - LOGGING_LEVEL_COM_MCPVIEWING=DEBUG
  - LOGGING_LEVEL_ORG_SPRINGFRAMEWORK=DEBUG
```

### 4. Sichere Nutzung

```bash
# Nur localhost-Zugriff
docker run -d \
  -p 127.0.0.1:8080:8080 \
  -p 127.0.0.1:9000:9000 \
  mcp-viewing:latest
```

## Weitere Ressourcen

- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Vollständiger Docker Deployment Guide
- **[README.md](README.md)** - Allgemeine Projektdokumentation
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - REST-API Beispiele
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Offizielle MCP Spezifikation
- **[Claude Desktop](https://claude.ai/download)** - Claude Desktop Download

## Support

Bei Problemen oder Fragen:

1. Überprüfen Sie die [Troubleshooting](#troubleshooting) Sektion
2. Prüfen Sie die Container-Logs: `docker-compose logs`
3. Testen Sie die Socket-Verbindung: `nc localhost 9000`
4. Erstellen Sie ein Issue im GitHub Repository
