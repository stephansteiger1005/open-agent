# Dokumentation zur Erstellung von GitHub-Zugriffstokens

Diese Dokumentation beschreibt die Erstellung von GitHub Personal Access Tokens (PAT) für verschiedene Zugriffsszenarien beim MCP_Viewing-Projekt.

## Übersicht

GitHub Personal Access Tokens ermöglichen den programmatischen Zugriff auf Repository-Ressourcen ohne Verwendung Ihres Passworts. Je nach Anwendungsfall benötigen Sie unterschiedliche Berechtigungen.

## Voraussetzungen

- Ein GitHub-Konto mit Zugriff auf das Repository
- Administratorrechte im Repository (für bestimmte Berechtigungen)
- Zwei-Faktor-Authentifizierung (2FA) aktiviert (empfohlen)

## Allgemeine Anleitung zur Token-Erstellung

### Schritt 1: Zu den Token-Einstellungen navigieren

1. Melden Sie sich bei GitHub an
2. Klicken Sie oben rechts auf Ihr Profilbild
3. Wählen Sie **Settings** (Einstellungen)
4. Scrollen Sie im linken Menü nach unten zu **Developer settings**
5. Wählen Sie **Personal access tokens**
6. Wählen Sie **Tokens (classic)** oder **Fine-grained tokens** (empfohlen)

**Hinweis:** Fine-grained tokens bieten granularere Kontrolle und sind sicherer. Wir empfehlen deren Verwendung.

### Schritt 2: Neuen Token erstellen

1. Klicken Sie auf **Generate new token** (für classic) oder **Generate new token** → **Fine-grained token** (empfohlen)
2. Geben Sie einen aussagekräftigen Namen ein (z.B. "Docker Pull Token", "Read-Only Repo Access")
3. Legen Sie ein Ablaufdatum fest (empfohlen: maximal 90 Tage)
4. Wählen Sie die erforderlichen Berechtigungen (siehe unten für spezifische Anwendungsfälle)
5. Klicken Sie auf **Generate token**
6. **Wichtig:** Kopieren Sie den Token sofort und speichern Sie ihn an einem sicheren Ort (z.B. Passwort-Manager). Der Token wird nur einmal angezeigt!

---

## Anwendungsfall 1: Ausschließlich Herunterladen von gebauten Docker-Containern

### Beschreibung

Dieser Token ermöglicht nur das Herunterladen (Pull) von Docker-Images aus der GitHub Container Registry. Kein Zugriff auf Quellcode oder andere Repository-Ressourcen.

### Berechtigungen für Fine-grained Token

**Repository access:**
- **Only select repositories** → Wählen Sie `iau4u/MCP_Viewing`

**Repository permissions:**
- Keine spezifischen Repository-Berechtigungen erforderlich

**Account permissions:**
- Keine erforderlich

**Hinweis:** Der Zugriff auf öffentliche Packages in GHCR erfordert keine speziellen Berechtigungen. Für private Packages:

### Berechtigungen für Classic Token

Wählen Sie folgende Bereiche:

- ✅ `read:packages` - Download packages from GitHub Package Registry

**Nicht erforderlich:**
- ❌ Alle anderen Berechtigungen

### Verwendung

```bash
# Bei GitHub Container Registry anmelden
echo "IHR_TOKEN" | docker login ghcr.io -u IHR_GITHUB_USERNAME --password-stdin

# Docker Image herunterladen
docker pull ghcr.io/iau4u/mcp-viewing:latest

# Container starten
docker run -p 8080:8080 ghcr.io/iau4u/mcp-viewing:latest
```

### Sicherheitshinweise

- Dieser Token gewährt **keinen** Zugriff auf den Quellcode
- Dieser Token kann **nicht** zum Hochladen von Packages verwendet werden
- Ideal für Produktionsumgebungen, in denen nur das fertige Image benötigt wird
- Token sollte in CI/CD-Systemen als Secret gespeichert werden

---

## Anwendungsfall 2: Zugriff auf das komplette Repository (nur lesend)

### Beschreibung

Dieser Token ermöglicht den lesenden Zugriff auf alle Repository-Inhalte: Quellcode, Issues, Pull Requests, Releases, Packages usw. Keine Schreibrechte.

### Berechtigungen für Fine-grained Token

**Repository access:**
- **Only select repositories** → Wählen Sie `iau4u/MCP_Viewing`

**Repository permissions:**
- **Contents** → `Read-only` (Zugriff auf Code, Commits, Branches, Tags)
- **Issues** → `Read-only` (optional, für Issue-Zugriff)
- **Pull requests** → `Read-only` (optional, für PR-Zugriff)
- **Metadata** → `Read-only` (automatisch ausgewählt)

**Optional (je nach Bedarf):**
- **Actions** → `Read-only` (für Zugriff auf Workflow-Runs)
- **Packages** → `Read-only` (für Docker-Images)

### Berechtigungen für Classic Token

Wählen Sie folgende Bereiche:

- ✅ `repo` (kompletter Zugriff auf private Repositories)
  - Automatisch enthalten: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

**Alternative (nur für öffentliche Repositories):**
- ✅ `public_repo` - Zugriff nur auf öffentliche Repositories

**Optional:**
- ✅ `read:packages` - Zugriff auf Packages
- ✅ `read:org` - Zugriff auf Organisationsdaten

### Verwendung

```bash
# Repository klonen
git clone https://IHR_GITHUB_USERNAME:IHR_TOKEN@github.com/iau4u/MCP_Viewing.git

# Oder: Token als Credential Helper konfigurieren
git config --global credential.helper store
echo "https://IHR_GITHUB_USERNAME:IHR_TOKEN@github.com" >> ~/.git-credentials

# Normale Git-Operationen
git clone https://github.com/iau4u/MCP_Viewing.git
cd MCP_Viewing
git fetch
git pull
git log
```

### GitHub CLI Verwendung

```bash
# Mit gh CLI anmelden
echo "IHR_TOKEN" | gh auth login --with-token

# Repository-Informationen abrufen
gh repo view iau4u/MCP_Viewing

# Issues auflisten
gh issue list

# Pull Requests anzeigen
gh pr list

# Release-Informationen
gh release list
```

### API-Verwendung

```bash
# GitHub REST API verwenden
curl -H "Authorization: token IHR_TOKEN" \
  https://api.github.com/repos/iau4u/MCP_Viewing

# Dateien abrufen
curl -H "Authorization: token IHR_TOKEN" \
  https://api.github.com/repos/iau4u/MCP_Viewing/contents/README.md
```

### Sicherheitshinweise

- Dieser Token ermöglicht **keinen** Push/Commit von Code
- Ideal für Continuous Integration (CI) Systeme zum Checkout
- Kann für Code-Review-Tools und Analyse-Software verwendet werden
- Für rein lesende Zugriffe in Entwicklungsumgebungen

---

## Anwendungsfall 3: Zugriff auf das komplette Repository (lesend und schreibend)

### Beschreibung

Dieser Token ermöglicht vollständigen Lese- und Schreibzugriff auf das Repository: Code-Änderungen, Commits, Branches, Issues, Pull Requests, Releases, Packages usw.

### Berechtigungen für Fine-grained Token

**Repository access:**
- **Only select repositories** → Wählen Sie `iau4u/MCP_Viewing`

**Repository permissions:**
- **Contents** → `Read and write` (Code, Commits, Branches, Tags)
- **Pull requests** → `Read and write` (PRs erstellen und bearbeiten)
- **Issues** → `Read and write` (optional, Issues erstellen/bearbeiten)
- **Metadata** → `Read-only` (automatisch)

**Optional (je nach Bedarf):**
- **Actions** → `Read and write` (Workflows triggern)
- **Packages** → `Read and write` (Docker-Images pushen)
- **Workflows** → `Read and write` (GitHub Actions Workflows bearbeiten)
- **Administration** → `Read and write` (nur für Repository-Administratoren)

### Berechtigungen für Classic Token

Wählen Sie folgende Bereiche:

- ✅ `repo` (kompletter Zugriff auf private Repositories)
  - Beinhaltet: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

**Optional (je nach Bedarf):**
- ✅ `workflow` - Update GitHub Action workflows
- ✅ `write:packages` - Upload packages to GitHub Package Registry
- ✅ `delete:packages` - Delete packages from GitHub Package Registry

**Für Repository-Administration:**
- ✅ `admin:repo_hook` - Vollständiger Zugriff auf Repository-Hooks
- ✅ `admin:org` - Vollständiger Zugriff auf Organisationen (nur wenn nötig)

### Verwendung

```bash
# Repository klonen
git clone https://IHR_GITHUB_USERNAME:IHR_TOKEN@github.com/iau4u/MCP_Viewing.git
cd MCP_Viewing

# Code ändern und committen
git add .
git commit -m "Meine Änderungen"
git push origin main

# Neuen Branch erstellen und pushen
git checkout -b feature/neue-funktion
git push -u origin feature/neue-funktion

# Tag erstellen und pushen
git tag v1.0.1
git push origin v1.0.1
```

### CI/CD Verwendung (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.PAT_TOKEN }}
      
      - name: Build and Push
        run: |
          # Build durchführen
          mvn clean package
          
          # Mit Docker Registry anmelden
          echo "${{ secrets.PAT_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          
          # Docker Image bauen und pushen
          docker build -t ghcr.io/iau4u/mcp-viewing:latest .
          docker push ghcr.io/iau4u/mcp-viewing:latest
```

### Package Publishing (Docker)

```bash
# Bei GitHub Container Registry anmelden
echo "IHR_TOKEN" | docker login ghcr.io -u IHR_GITHUB_USERNAME --password-stdin

# Image bauen
docker build -t ghcr.io/iau4u/mcp-viewing:latest .

# Image pushen
docker push ghcr.io/iau4u/mcp-viewing:latest
```

### Sicherheitshinweise

- ⚠️ **Höchste Vorsicht:** Dieser Token hat vollständige Schreibrechte!
- Niemals in öffentlichem Code committen
- Nur in vertrauenswürdigen CI/CD-Systemen verwenden
- Regelmäßig rotieren (alle 30-60 Tage)
- Sofort widerrufen bei Kompromittierung
- Nutzen Sie Fine-grained Tokens mit minimalen Berechtigungen
- Erwägen Sie die Verwendung von GitHub Apps für CI/CD (noch sicherer)

---

## Best Practices für Token-Sicherheit

### 1. Token-Management

- **Aussagekräftige Namen:** Benennen Sie Tokens nach Verwendungszweck (z.B. "CI-Docker-Push", "Dev-ReadOnly")
- **Ablaufdatum setzen:** Tokens sollten nach maximal 90 Tagen ablaufen
- **Minimale Berechtigungen:** Vergeben Sie nur die absolut notwendigen Rechte (Principle of Least Privilege)
- **Fine-grained Tokens bevorzugen:** Nutzen Sie die neueren Fine-grained Tokens für bessere Kontrolle
- **Regelmäßige Rotation:** Wechseln Sie Tokens regelmäßig, besonders bei Schreibrechten

### 2. Token-Speicherung

- **Niemals im Code:** Tokens dürfen niemals in Git committed werden
- **Passwort-Manager:** Speichern Sie Tokens in einem Passwort-Manager (z.B. 1Password, LastPass, Bitwarden)
- **Umgebungsvariablen:** Nutzen Sie Umgebungsvariablen in Skripten
- **CI/CD Secrets:** Verwenden Sie die Secret-Management-Funktionen Ihrer CI/CD-Plattform
- **Verschlüsselte Speicherung:** Falls lokale Speicherung nötig, verwenden Sie verschlüsselte Dateien

```bash
# Beispiel: Token als Umgebungsvariable
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
git clone https://${GITHUB_TOKEN}@github.com/iau4u/MCP_Viewing.git

# Token nicht in der Shell-History speichern
export HISTIGNORE="export GITHUB_TOKEN*"
```

### 3. Token-Verwendung

- **HTTPS verwenden:** Nutzen Sie immer HTTPS, niemals HTTP
- **Nicht in Logs:** Stellen Sie sicher, dass Tokens nicht in Logs erscheinen
- **Zeitlich begrenzen:** Verwenden Sie Tokens nur für die Dauer der Aufgabe
- **Widerrufen nach Verwendung:** Nicht mehr benötigte Tokens sofort löschen

### 4. Kompromittierung

**Wenn ein Token kompromittiert wurde:**

1. **Sofort widerrufen:**
   - Gehen Sie zu Settings → Developer settings → Personal access tokens
   - Klicken Sie auf "Delete" beim kompromittierten Token

2. **Aktivitäten überprüfen:**
   - Überprüfen Sie die Audit-Logs des Repositories
   - Suchen Sie nach verdächtigen Commits oder Änderungen

3. **Neuen Token erstellen:**
   - Erstellen Sie einen neuen Token mit gleichen Berechtigungen
   - Aktualisieren Sie alle Systeme, die den alten Token verwendet haben

4. **Incident melden:**
   - Informieren Sie Ihr Security-Team
   - Dokumentieren Sie den Vorfall

### 5. Git Credential Helper

Für lokale Entwicklung empfehlen wir den Git Credential Helper:

```bash
# Credential Helper konfigurieren (speichert Token sicher)
git config --global credential.helper cache

# Token-Gültigkeit auf 1 Stunde begrenzen
git config --global credential.helper 'cache --timeout=3600'

# Oder: Credential Helper mit OS-Keychain (macOS/Windows)
# macOS
git config --global credential.helper osxkeychain

# Windows
git config --global credential.helper manager

# Linux (libsecret)
git config --global credential.helper libsecret
```

---

## Fehlerbehebung

### Problem: "Authentication failed" beim Git Clone/Push

**Symptom:**
```
remote: Invalid username or password.
fatal: Authentication failed for 'https://github.com/iau4u/MCP_Viewing.git/'
```

**Lösungen:**
1. Überprüfen Sie, ob der Token noch gültig ist (nicht abgelaufen)
2. Stellen Sie sicher, dass Sie den Token korrekt verwenden:
   ```bash
   git clone https://IHR_USERNAME:IHR_TOKEN@github.com/iau4u/MCP_Viewing.git
   ```
3. Überprüfen Sie, ob der Token die erforderlichen Berechtigungen hat
4. Löschen Sie zwischengespeicherte Credentials:
   ```bash
   git credential-cache exit
   ```

### Problem: "Resource not accessible" bei Package Download

**Symptom:**
```
Error response from daemon: unauthorized: authentication required
```

**Lösungen:**
1. Stellen Sie sicher, dass der Token `read:packages` Berechtigung hat
2. Melden Sie sich korrekt bei GHCR an:
   ```bash
   echo "IHR_TOKEN" | docker login ghcr.io -u IHR_USERNAME --password-stdin
   ```
3. Überprüfen Sie die Package-Sichtbarkeit (öffentlich vs. privat)

### Problem: "Permission denied" beim Push

**Symptom:**
```
remote: Permission to iau4u/MCP_Viewing.git denied to USERNAME.
fatal: unable to access 'https://github.com/iau4u/MCP_Viewing.git/': The requested URL returned error: 403
```

**Lösungen:**
1. Überprüfen Sie, ob der Token Schreibrechte hat (`repo` für Classic oder `Contents: Read and write` für Fine-grained)
2. Stellen Sie sicher, dass Sie als der richtige Benutzer authentifiziert sind
3. Überprüfen Sie, ob Branch-Protection-Rules einen direkten Push verhindern

### Problem: Token wird in Shell-History gespeichert

**Lösung:**
```bash
# Token nicht in History speichern
export HISTIGNORE="export GITHUB_TOKEN*:git clone*token*:echo*token*"

# Oder: History temporär deaktivieren
set +o history
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
set -o history
```

### Problem: Fine-grained Token funktioniert nicht mit Git

**Hinweis:** Fine-grained Tokens werden möglicherweise noch nicht von allen Git-Operationen unterstützt. In diesem Fall:

1. Verwenden Sie einen Classic Token für Git-Operationen
2. Verwenden Sie Fine-grained Tokens für API-Zugriffe
3. Überprüfen Sie die GitHub-Dokumentation auf Updates

---

## Zusammenfassung der Berechtigungen

| Anwendungsfall | Classic Token | Fine-grained Token | Beschreibung |
|----------------|---------------|-------------------|--------------|
| **Docker Pull** | `read:packages` | Packages: Read-only | Nur Docker-Images herunterladen |
| **Repo Read-Only** | `repo` (für private) oder `public_repo` | Contents: Read-only | Code lesen, keine Änderungen |
| **Repo Read-Write** | `repo` + optional `workflow`, `write:packages` | Contents: Read and write, PR: Read and write, optional: Packages: Read and write | Vollständiger Zugriff |

---

## Weiterführende Ressourcen

- [GitHub Docs: Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Docs: About permissions for GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-permissions-for-github-apps)
- [GitHub Container Registry Dokumentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Git Credential Storage](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)

---

## Support

Bei Fragen oder Problemen:

- **Issues:** Erstellen Sie ein Issue im Repository
- **Security:** Bei Sicherheitsproblemen siehe [SECURITY.md](SECURITY.md)
- **Kontakt:** MCP Viewing Team - support@mcpviewing.com

---

**Letzte Aktualisierung:** Januar 2026
**Version:** 1.0
