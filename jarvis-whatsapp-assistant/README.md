# 🤖 JARVIS WhatsApp Assistant

Ein intelligenter KI-Assistent für WhatsApp, inspiriert von JARVIS aus Iron Man. Kann Aufgaben wie Blumenbestellungen, Terminplanung und vieles mehr automatisch ausführen.

## ✨ Features

- 🎤 **Spracherkennung** - Versteht Sprachnachrichten
- 🧠 **KI-gesteuert** - Nutzt OpenAI GPT-4 für intelligente Antworten
- 🌹 **E-Commerce Integration** - Kann echte Bestellungen aufgeben
- 📱 **WhatsApp Integration** - Funktioniert direkt über WhatsApp
- 🔄 **Kontextbewusst** - Merkt sich Unterhaltungen
- 🚀 **Skalierbar** - Bereit für Produktionseinsatz

## 🚀 Schnellstart

### Voraussetzungen

- Docker und Docker Compose
- Meta Developer Account
- OpenAI API Account
- Google Cloud Account (optional, für Spracherkennung)

### 1. Repository klonen

```bash
git clone <repository-url>
cd jarvis-whatsapp-assistant
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
# Bearbeiten Sie .env mit Ihren API-Schlüsseln
```

### 3. Mit Setup-Skript starten

```bash
./scripts/setup.sh
```

Wählen Sie Option 1 für lokale Entwicklung oder Option 2 für Produktionsdeployment.

## 📋 Manuelle Einrichtung

### WhatsApp Business API einrichten

1. **Meta Developer Account erstellen**
   - Gehen Sie zu [developers.facebook.com](https://developers.facebook.com)
   - Erstellen Sie einen Account und eine neue App
   - Fügen Sie das WhatsApp-Produkt hinzu

2. **Webhook konfigurieren**
   - Webhook URL: `https://ihre-domain.com/api/v1/webhook`
   - Verify Token: Ihr gewählter Token aus `.env`

3. **Telefonnummer hinzufügen**
   - Fügen Sie Ihre WhatsApp Business Nummer hinzu
   - Verifizieren Sie die Nummer

### OpenAI API einrichten

1. Gehen Sie zu [platform.openai.com](https://platform.openai.com)
2. Erstellen Sie einen Account
3. Generieren Sie einen API-Schlüssel
4. Fügen Sie den Schlüssel in `.env` ein

### Google Cloud (optional)

1. Erstellen Sie ein Google Cloud Projekt
2. Aktivieren Sie Speech-to-Text und Text-to-Speech APIs
3. Erstellen Sie einen Service Account
4. Laden Sie die JSON-Datei herunter

## 🐳 Docker Deployment

### Lokal mit Docker Compose

```bash
docker-compose up -d
```

Die Anwendung läuft dann auf `http://localhost:8000`

### Produktionsdeployment

```bash
# Image bauen
docker build -t jarvis-backend:latest .

# In Container Registry pushen
docker tag jarvis-backend:latest gcr.io/YOUR_PROJECT/jarvis-backend:latest
docker push gcr.io/YOUR_PROJECT/jarvis-backend:latest
```

## ☸️ Kubernetes Deployment

### Google Kubernetes Engine

```bash
# Cluster erstellen
gcloud container clusters create jarvis-cluster \
  --zone=us-central1-a \
  --num-nodes=3

# Credentials holen
gcloud container clusters get-credentials jarvis-cluster --zone=us-central1-a

# Secrets erstellen
kubectl create secret generic jarvis-secrets --from-env-file=.env

# Deployen
kubectl apply -f k8s/
```

## 🔧 Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Erforderlich |
|----------|--------------|--------------|
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp API Token | ✅ |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp Telefonnummer ID | ✅ |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Webhook Verify Token | ✅ |
| `OPENAI_API_KEY` | OpenAI API Schlüssel | ✅ |
| `GOOGLE_CLOUD_PROJECT_ID` | Google Cloud Projekt ID | ❌ |
| `DATABASE_URL` | PostgreSQL Verbindung | ❌ |
| `REDIS_URL` | Redis Verbindung | ❌ |

### Features konfigurieren

- **Spracherkennung**: Konfigurieren Sie Google Cloud Credentials
- **E-Commerce**: Fügen Sie Shopify API-Schlüssel hinzu
- **Monitoring**: Aktivieren Sie Prometheus Metriken

## 📊 Monitoring

### Prometheus Metriken

Die Anwendung exportiert Metriken auf `/metrics`:

- `jarvis_messages_processed_total` - Anzahl verarbeiteter Nachrichten
- `jarvis_response_time_seconds` - Antwortzeiten
- `jarvis_active_users` - Aktive Benutzer
- `jarvis_errors_total` - Fehleranzahl

### Grafana Dashboard

Ein vorkonfiguriertes Dashboard ist in `monitoring/grafana-dashboard.json` verfügbar.

## 🧪 Testing

### Webhook testen

```bash
curl -X POST http://localhost:8000/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "field": "messages",
        "value": {
          "messages": [{
            "from": "1234567890",
            "id": "msg123",
            "type": "text",
            "text": {"body": "Hallo JARVIS"},
            "timestamp": "1234567890"
          }]
        }
      }]
    }]
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🔒 Sicherheit

- Alle API-Schlüssel werden als Kubernetes Secrets gespeichert
- HTTPS wird durch Nginx und Let's Encrypt erzwungen
- Rate Limiting verhindert Missbrauch
- Input Validation schützt vor Injection-Angriffen

## 📝 API Dokumentation

### Webhook Endpunkte

- `GET /api/v1/webhook` - Webhook Verifizierung
- `POST /api/v1/webhook` - Nachrichten empfangen

### Utility Endpunkte

- `GET /` - API Information
- `GET /health` - Health Check
- `GET /metrics` - Prometheus Metriken

## 🤝 Beitragen

1. Fork das Repository
2. Erstellen Sie einen Feature Branch
3. Committen Sie Ihre Änderungen
4. Pushen Sie den Branch
5. Erstellen Sie einen Pull Request

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei.

## 🆘 Support

- 📖 [Dokumentation](docs/)
- 🐛 [Issues](https://github.com/your-repo/issues)
- 💬 [Diskussionen](https://github.com/your-repo/discussions)

## 🎯 Roadmap

- [ ] Mehrsprachige Unterstützung
- [ ] Erweiterte E-Commerce Integration
- [ ] Smart Home Integration
- [ ] Voice Responses
- [ ] Sentiment Analysis
- [ ] Custom Training Data

---

**Erstellt mit ❤️ für die Zukunft der KI-Assistenten**
