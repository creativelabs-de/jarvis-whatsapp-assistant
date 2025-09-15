# 🚀 GitHub Setup für JARVIS WhatsApp Assistant

Diese Anleitung hilft Ihnen dabei, Ihr JARVIS Projekt auf GitHub zu veröffentlichen und zu deployen.

## 📋 Voraussetzungen

- ✅ GitHub Account erstellt
- ✅ Git auf Ihrem Computer installiert
- ✅ Dieses Projekt heruntergeladen

## 🔧 Schritt 1: Repository auf GitHub erstellen

1. **Gehen Sie zu GitHub:** https://github.com
2. **Klicken Sie auf:** "New repository" (grüner Button)
3. **Repository Name:** `jarvis-whatsapp-assistant`
4. **Beschreibung:** `🤖 Intelligenter WhatsApp KI-Assistent wie JARVIS aus Iron Man`
5. **Sichtbarkeit:** Private (empfohlen) oder Public
6. **NICHT ankreuzen:** "Add a README file" (haben wir schon)
7. **Klicken Sie:** "Create repository"

## 📤 Schritt 2: Code zu GitHub hochladen

Öffnen Sie ein Terminal/Kommandozeile in Ihrem Projektordner und führen Sie aus:

```bash
# Git konfigurieren (nur beim ersten Mal)
git config --global user.name "Ihr Name"
git config --global user.email "ihre-email@example.com"

# Alle Dateien hinzufügen
git add .

# Ersten Commit erstellen
git commit -m "🤖 Initial JARVIS WhatsApp Assistant implementation

✨ Features:
- WhatsApp Cloud API integration
- OpenAI GPT-4 powered conversations
- Speech-to-text recognition
- E-commerce flower ordering
- Docker & Kubernetes deployment
- Complete CI/CD pipeline"

# GitHub Repository als Remote hinzufügen
git remote add origin https://github.com/creativelabs-de/jarvis-whatsapp-assistant.git

# Code hochladen
git branch -M main
git push -u origin main
```

**Repository URL ist bereits konfiguriert für: creativelabs-de**

## 🔐 Schritt 3: GitHub Secrets konfigurieren

Für automatische Deployments müssen Sie Secrets in GitHub einrichten:

1. **Gehen Sie zu Ihrem Repository**
2. **Klicken Sie:** Settings → Secrets and variables → Actions
3. **Fügen Sie diese Secrets hinzu:**

| Secret Name | Beschreibung | Beispiel |
|-------------|--------------|----------|
| `GCP_PROJECT_ID` | Google Cloud Projekt ID | `jarvis-assistant-2024` |
| `GCP_SA_KEY` | Google Cloud Service Account JSON | `{"type": "service_account"...}` |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp API Token | `EAAxxxxx...` |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp Telefonnummer ID | `123456789` |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Webhook Verify Token | `jarvis_secure_token_2024` |
| `OPENAI_API_KEY` | OpenAI API Schlüssel | `sk-xxxxx...` |
| `SLACK_WEBHOOK` | Slack Webhook für Benachrichtigungen | `https://hooks.slack.com/...` |

## 🌐 Schritt 4: GitHub Pages aktivieren (optional)

Für eine einfache Dokumentations-Website:

1. **Repository Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** main
4. **Folder:** / (root)
5. **Save**

Ihre Dokumentation ist dann verfügbar unter:
`https://creativelabs-de.github.io/jarvis-whatsapp-assistant/`

## 🚀 Schritt 5: Automatisches Deployment

Nach dem Push wird automatisch:

1. **Tests ausgeführt** (GitHub Actions)
2. **Docker Image gebaut** und zu Google Container Registry gepusht
3. **Staging-Deployment** durchgeführt
4. **Production-Deployment** (nach manueller Freigabe)

## 📊 Schritt 6: Monitoring einrichten

1. **GitHub Actions** → Workflows → CI/CD Pipeline
2. **Überprüfen Sie:** Test-Ergebnisse und Deployment-Status
3. **Aktivieren Sie:** E-Mail-Benachrichtigungen bei Fehlern

## 🔧 Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/creativelabs-de/jarvis-whatsapp-assistant.git
cd jarvis-whatsapp-assistant

# Umgebung einrichten
cp .env.example .env
# .env mit Ihren API-Schlüsseln bearbeiten

# Lokal starten
./scripts/setup.sh
```

## 🆘 Troubleshooting

### Problem: "Permission denied" beim Push
```bash
# GitHub Personal Access Token erstellen und verwenden
git remote set-url origin https://IHR-TOKEN@github.com/creativelabs-de/jarvis-whatsapp-assistant.git
```

### Problem: Tests schlagen fehl
```bash
# Lokal testen
./scripts/run_tests.sh
```

### Problem: Deployment schlägt fehl
1. Überprüfen Sie GitHub Secrets
2. Kontrollieren Sie Google Cloud Berechtigungen
3. Schauen Sie in GitHub Actions Logs

## 📞 Support

- 📖 [Vollständige Dokumentation](README.md)
- 🐛 [Issues erstellen](https://github.com/creativelabs-de/jarvis-whatsapp-assistant/issues)
- 💬 [Diskussionen](https://github.com/creativelabs-de/jarvis-whatsapp-assistant/discussions)

## 🎉 Nächste Schritte

Nach erfolgreichem Setup:

1. ✅ WhatsApp Webhook konfigurieren
2. ✅ Erste Testnachricht senden
3. ✅ Monitoring überprüfen
4. ✅ Features erweitern

**Viel Erfolg mit Ihrem JARVIS Assistant! 🤖**
