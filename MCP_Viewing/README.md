# MCP_Viewing

Spring Boot Backend für PLMXML-Datenverwaltung mit Derby-Datenbank und MCP-Unterstützung

## Übersicht

MCP_Viewing ist eine REST-API-basierte Backend-Anwendung, die mit Spring Boot entwickelt wurde. Sie ermöglicht die Verwaltung von PLMXML-Daten in einer Derby-Datenbank (PARTINFODB), wobei Sachnummern (SNR) als eindeutige Schlüssel dienen.

**NEU:** Das Projekt unterstützt jetzt das **Model Context Protocol (MCP)** von Anthropic:
- **HTTP/SSE Transport** - für OpenAI Proxy und OpenWebUI
- **Socket Transport** - für Claude Desktop
- **Stdio Transport** - für direkte Integration

## Features

- ✅ REST API mit vier Hauptendpunkten:
  1. **GET** `/api/partinfo/{sachnummer}` - Herunterladen der neuesten PLMXML-Datei (höchste Revision/Sequenz) nach Sachnummer
  2. **GET** `/api/partinfo/{sachnummer}/{revision}/{sequenz}` - Herunterladen einer spezifischen PLMXML-Datei
  3. **POST** `/api/partinfo` - Erstellen oder Aktualisieren eines Eintrags
  4. **DELETE** `/api/partinfo/{sachnummer}/{revision}/{sequenz}` - Löschen eines Eintrags

- ✅ **MCP (Model Context Protocol) Server:**
  - **HTTP/SSE Transport** für OpenAI Proxy und OpenWebUI
  - **Socket Transport** für Claude Desktop
  - **Stdio Transport** für direkte Integration
  - 4 MCP-Tools für PLMXML-Verwaltung
  - JSON-RPC 2.0 Protokoll
  - CORS-Unterstützung für Web-Clients
  - Siehe [MCP_INTEGRATION.md](MCP_INTEGRATION.md) für Details

- ✅ Derby-Datenbank (PARTINFODB) mit Hibernate/JPA
- ✅ Swagger/OpenAPI-Dokumentation unter `/swagger-ui.html`
- ✅ Vollständige Test-Suite (Unit- und Integrationstests)
- ✅ Docker-Support mit Multi-Stage Build
- ✅ **Docker Container Status-Checker** - Umfassendes Diagnose-Script für Container-Zustand
- ✅ CI/CD-Pipelines (Jenkins & GitHub Actions)

## Technologie-Stack

- **Java**: 17
- **Framework**: Spring Boot 3.2.1
- **Datenbank**: Apache Derby (Embedded)
- **ORM**: Hibernate/JPA
- **API-Dokumentation**: SpringDoc OpenAPI (Swagger)
- **Build-Tool**: Maven 3.9.5
- **Container**: Docker
- **CI/CD**: Jenkins + GitHub Actions
- **MCP**: Model Context Protocol v0.1.0 (JSON-RPC 2.0)

## Datenbankschema

Die Anwendung verwendet das vollständige PartInfo-Schema aus dem MIDGUARD-Projekt:

```sql
CREATE TABLE PartInfo (
    obsoleteEntry SMALLINT,
    clazz VARCHAR(16) NOT NULL,
    sachnummer VARCHAR(32) NOT NULL,
    revision INTEGER NOT NULL,
    sequenz INTEGER NOT NULL,
    owner VARCHAR(32),
    status VARCHAR(16),
    frozen SMALLINT,
    nomenclature VARCHAR(256),
    changeDescription VARCHAR(256),
    checksum3D BIGINT,
    checksum2D BIGINT,
    checksumBOM BIGINT,
    plmxml BLOB,
    PRIMARY KEY (sachnummer, revision, sequenz)
);
```

**Wichtig**: Die PLMXML-Daten werden im zlib-Format komprimiert in der Datenbank gespeichert. Die API übernimmt automatisch:
- **Bei Eingabe**: Base64-Dekodierung → zlib-Kompression → Speicherung als BLOB
- **Bei Ausgabe**: BLOB-Abruf → zlib-Dekompression → Rückgabe als herunterladbare XML-Datei

## Voraussetzungen

- Java 17 oder höher
- Maven 3.6+
- Docker (optional, für Container-Deployment)
- Jenkins (optional, für CI/CD)
- **GitHub Access Token** (für Docker Registry oder Repository-Zugriff) - Siehe [TOKEN_CREATION.md](TOKEN_CREATION.md)

## Installation & Start

### Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/iau4u/MCP_Viewing.git
cd MCP_Viewing

# Abhängigkeiten installieren und Build ausführen
mvn clean install

# Anwendung starten
mvn spring-boot:run
```

Die Anwendung läuft auf `http://localhost:8080`

### Mit Docker

```bash
# Docker Image bauen
docker build -t mcp-viewing .

# Container starten
docker run -p 8080:8080 mcp-viewing
```

### Mit Docker Compose

```bash
docker-compose up -d
```

### Docker Container Status prüfen

Um den aktuellen Zustand des Docker-Containers zu überprüfen:

```bash
./check-docker-status.sh
```

Dieses Script überprüft:
- Docker-Verfügbarkeit
- Container-Existenz und Status
- Port-Mappings
- Health Check Status
- Ressourcennutzung
- REST-API und MCP-Server Konnektivität
- Aktuelle Logs

## MCP Server (Claude Desktop Integration)

Das Projekt kann als MCP-Server mit Claude Desktop verwendet werden:

### Schnellstart

```bash
# 1. JAR-Datei erstellen
mvn clean package -DskipTests

# 2. Claude Desktop konfigurieren
# Bearbeiten Sie ~/.config/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "mcp-viewing": {
      "command": "java",
      "args": [
        "-jar",
        "/absoluter/pfad/zu/target/mcp-viewing-1.0.0.jar",
        "--mcp.server.enabled=true",
        "--spring.main.web-application-type=none"
      ]
    }
  }
}

# 3. Claude Desktop neu starten
```

### Verfügbare MCP-Tools

- `get_partinfo_latest` - Neueste PLMXML-Daten nach Sachnummer abrufen
- `get_partinfo_specific` - Spezifische PLMXML-Version abrufen
- `create_partinfo` - PLMXML-Daten erstellen/aktualisieren
- `delete_partinfo` - PLMXML-Daten löschen

**Vollständige Dokumentation:** Siehe [MCP_INTEGRATION.md](MCP_INTEGRATION.md)

## API-Dokumentation

Nach dem Start ist die Swagger-UI verfügbar unter:
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **OpenAPI Docs**: http://localhost:8080/api-docs

### Beispiel-Requests

#### 1. PartInfo erstellen

```bash
curl -X POST http://localhost:8080/api/partinfo \
  -H "Content-Type: application/json" \
  -d '{
    "obsoleteEntry": 0,
    "clazz": "Part",
    "sachnummer": "PART-001",
    "revision": 1,
    "sequenz": 1,
    "owner": "Engineering",
    "status": "Active",
    "frozen": 0,
    "nomenclature": "Test Part",
    "changeDescription": "Initial creation",
    "checksum3D": 123456,
    "checksum2D": 789012,
    "checksumBOM": 345678,
    "plmxml": "PFBMTVhNTD5UZXN0IERhdGE8L1BMTVhNTD4="
  }'
```

#### 2. Neueste Version nach Sachnummer abrufen

```bash
curl http://localhost:8080/api/partinfo/PART-001 -o PART-001.plmxml
```

Gibt die PLMXML-Datei mit der höchsten Revision und Sequenz als Download zurück.

#### 3. Spezifische Version abrufen

```bash
curl http://localhost:8080/api/partinfo/PART-001/1/1 -o PART-001_1_1.plmxml
```

#### 4. PartInfo löschen

```bash
curl -X DELETE http://localhost:8080/api/partinfo/PART-001/1/1
```

**Hinweis**: PLMXML-Daten müssen Base64-kodiert übertragen werden.

## Tests

### Unit-Tests ausführen

```bash
mvn test
```

### Integration-Tests ausführen

```bash
mvn verify
```

### Test-Coverage-Report

```bash
mvn clean test jacoco:report
```

Der Coverage-Report ist verfügbar unter: `target/site/jacoco/index.html`

## CI/CD

### Jenkins Pipeline

Das Projekt enthält ein `Jenkinsfile` für Jenkins CI/CD:

**Pipeline-Schritte:**
1. Code Checkout
2. Build
3. Tests ausführen
4. Anwendung paketieren
5. Docker Image bauen
6. Docker Image testen
7. Docker Image pushen (nur main Branch)
8. Deployment (nur main Branch)

**Jenkins-Konfiguration:**
- Erstellen Sie einen neuen Pipeline-Job in Jenkins
- Repository-URL: `https://github.com/iau4u/MCP_Viewing.git`
- Script Path: `Jenkinsfile`
- Erforderliche Jenkins-Plugins:
  - Docker Pipeline Plugin
  - JaCoCo Plugin
  - Maven Integration Plugin

### GitHub Actions

Die GitHub Actions Workflows befinden sich in `.github/workflows/ci-cd.yml`:

**Workflows:**
1. **build-and-test**: Kompiliert, testet und paketiert die Anwendung
2. **docker-build**: Baut und pusht Docker Images
3. **integration-test**: Führt Integrationstests aus

**Erforderliche GitHub Secrets:**
- `DOCKER_USERNAME`: Docker Hub Benutzername
- `DOCKER_PASSWORD`: Docker Hub Passwort/Token

## Projektstruktur

```
MCP_Viewing/
├── src/
│   ├── main/
│   │   ├── java/com/mcpviewing/
│   │   │   ├── config/          # Konfigurationsklassen
│   │   │   ├── controller/      # REST Controller
│   │   │   ├── dto/             # Data Transfer Objects
│   │   │   ├── exception/       # Exception Handler
│   │   │   ├── model/           # JPA Entities
│   │   │   ├── repository/      # JPA Repositories
│   │   │   ├── service/         # Business Logic
│   │   │   └── McpViewingApplication.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
│       ├── java/com/mcpviewing/
│       │   ├── controller/      # Controller Tests
│       │   ├── integration/     # Integration Tests
│       │   └── service/         # Service Tests
│       └── resources/
│           └── application.properties
├── .github/workflows/           # GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile                  # Jenkins Pipeline
├── pom.xml
└── README.md
```

## Konfiguration

### Datenbank-Konfiguration

Die Datenbank wird automatisch beim Start erstellt (In-Memory Derby):

```properties
spring.datasource.url=jdbc:derby:memory:PARTINFODB;create=true
spring.jpa.hibernate.ddl-auto=update
```

Für Produktionsumgebungen kann eine persistente Derby-Datenbank konfiguriert werden:

```properties
spring.datasource.url=jdbc:derby:/path/to/PARTINFODB;create=true
```

## Gesundheitscheck

### Docker Container Status

Schnelle und umfassende Überprüfung des Docker-Container-Zustands:

```bash
./check-docker-status.sh
```

Für Details siehe [DOCKER_GUIDE.md](DOCKER_GUIDE.md#schnelle-status-überprüfung).

### REST API Gesundheitscheck

Der Actuator-Endpunkt für Gesundheitschecks:

```bash
curl http://localhost:8080/actuator/health
```

## Lizenz

Apache License 2.0

## Kontakt

MCP Viewing Team - support@mcpviewing.com

## Troubleshooting

### Docker Container Probleme

Verwenden Sie das Status-Check-Script für schnelle Diagnose:

```bash
./check-docker-status.sh
```

Vollständige Docker-Troubleshooting-Anleitung: [DOCKER_GUIDE.md](DOCKER_GUIDE.md#troubleshooting)

### Derby-Datenbank-Fehler

Wenn Derby-Fehler auftreten, löschen Sie die Datenbankdateien:
```bash
rm -rf derby.log *.lck *.properties
```

### Port bereits in Verwendung

Ändern Sie den Port in `application.properties`:
```properties
server.port=8081
```

### Maven Build-Fehler

Cache leeren und neu bauen:
```bash
mvn clean install -U
```
