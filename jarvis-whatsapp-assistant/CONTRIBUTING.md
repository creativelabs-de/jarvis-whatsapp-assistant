# 🤝 Contributing to JARVIS WhatsApp Assistant

Vielen Dank für Ihr Interesse, zu JARVIS beizutragen! Jeder Beitrag ist willkommen.

## 🚀 Wie Sie beitragen können

### 🐛 Bug Reports
- Verwenden Sie GitHub Issues
- Beschreiben Sie das Problem detailliert
- Fügen Sie Schritte zur Reproduktion hinzu
- Geben Sie Ihre Umgebung an (OS, Python Version, etc.)

### ✨ Feature Requests
- Öffnen Sie ein GitHub Issue
- Beschreiben Sie den gewünschten Feature
- Erklären Sie den Anwendungsfall
- Diskutieren Sie die Implementierung

### 🔧 Code Contributions

#### Setup für Entwicklung
```bash
# Repository forken und klonen
git clone https://github.com/IHR-BENUTZERNAME/jarvis-whatsapp-assistant.git
cd jarvis-whatsapp-assistant

# Development Environment einrichten
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

pip install -r backend/requirements.txt
pip install -r backend/test-requirements.txt
```

#### Code Standards
- **Python Style:** PEP 8 (verwenden Sie `black` und `flake8`)
- **Imports:** Sortiert mit `isort`
- **Type Hints:** Verwenden Sie Type Hints wo möglich
- **Docstrings:** Google Style Docstrings
- **Tests:** Schreiben Sie Tests für neue Features

#### Pre-commit Hooks
```bash
# Pre-commit installieren
pip install pre-commit
pre-commit install

# Manuell ausführen
pre-commit run --all-files
```

#### Testing
```bash
# Alle Tests ausführen
./scripts/run_tests.sh

# Spezifische Tests
cd backend
pytest tests/test_specific.py -v

# Mit Coverage
pytest --cov=app tests/
```

### 📝 Pull Request Prozess

1. **Fork** das Repository
2. **Branch erstellen:** `git checkout -b feature/amazing-feature`
3. **Änderungen committen:** `git commit -m 'Add amazing feature'`
4. **Tests ausführen:** `./scripts/run_tests.sh`
5. **Push:** `git push origin feature/amazing-feature`
6. **Pull Request öffnen**

#### Pull Request Guidelines
- **Titel:** Klarer, beschreibender Titel
- **Beschreibung:** Was wurde geändert und warum
- **Tests:** Alle Tests müssen bestehen
- **Documentation:** Aktualisieren Sie die Dokumentation
- **Changelog:** Fügen Sie Änderungen zur CHANGELOG.md hinzu

## 🏗️ Projekt Struktur

```
jarvis-whatsapp-assistant/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API Endpoints
│   │   ├── core/           # Core Konfiguration
│   │   ├── models/         # Datenmodelle
│   │   └── services/       # Business Logic
│   ├── tests/              # Test Suite
│   └── main.py             # Anwendungsstart
├── k8s/                    # Kubernetes Manifests
├── monitoring/             # Monitoring Konfiguration
├── scripts/                # Utility Scripts
└── docs/                   # Dokumentation
```

## 🧪 Testing Guidelines

### Unit Tests
- Testen Sie einzelne Funktionen/Methoden
- Verwenden Sie Mocks für externe Dependencies
- Mindestens 80% Code Coverage

### Integration Tests
- Testen Sie API Endpoints
- Verwenden Sie Test-Datenbank
- Testen Sie Service-Interaktionen

### End-to-End Tests
- Testen Sie komplette User Journeys
- Verwenden Sie echte WhatsApp Webhooks (Staging)

## 📚 Dokumentation

### Code Dokumentation
```python
def process_message(message: str, context: Dict) -> Dict:
    """Process incoming WhatsApp message.
    
    Args:
        message: The incoming message text
        context: User conversation context
        
    Returns:
        Dict containing response and updated context
        
    Raises:
        ProcessingError: If message processing fails
    """
```

### API Dokumentation
- FastAPI generiert automatisch OpenAPI Docs
- Verfügbar unter `/docs` und `/redoc`
- Halten Sie Docstrings aktuell

## 🔒 Security Guidelines

### Sensitive Data
- **Niemals** API-Keys oder Secrets committen
- Verwenden Sie `.env` Dateien (nicht versioniert)
- Nutzen Sie GitHub Secrets für CI/CD

### Input Validation
- Validieren Sie alle User Inputs
- Verwenden Sie Pydantic Models
- Sanitizen Sie Outputs

### Dependencies
- Halten Sie Dependencies aktuell
- Verwenden Sie `safety` für Security Scans
- Überprüfen Sie neue Dependencies

## 🌍 Internationalization

### Sprachen hinzufügen
1. Erstellen Sie Sprachdateien in `app/locales/`
2. Aktualisieren Sie die NLU Engine
3. Fügen Sie Tests hinzu
4. Dokumentieren Sie die Änderungen

## 🚀 Release Prozess

### Versioning
- Verwenden Sie [Semantic Versioning](https://semver.org/)
- Format: `MAJOR.MINOR.PATCH`
- Beispiel: `1.2.3`

### Release Checklist
- [ ] Alle Tests bestehen
- [ ] Dokumentation aktualisiert
- [ ] CHANGELOG.md aktualisiert
- [ ] Version in `__init__.py` erhöht
- [ ] Git Tag erstellt
- [ ] GitHub Release erstellt

## 💬 Community

### Kommunikation
- **GitHub Issues:** Bug Reports, Feature Requests
- **GitHub Discussions:** Allgemeine Fragen, Ideen
- **Pull Requests:** Code Reviews, Diskussionen

### Code of Conduct
- Seien Sie respektvoll und inklusiv
- Konstruktive Kritik ist willkommen
- Helfen Sie anderen Entwicklern
- Folgen Sie dem [Contributor Covenant](https://www.contributor-covenant.org/)

## 🎯 Roadmap

### Kurzfristig (nächste 3 Monate)
- [ ] Mehrsprachige Unterstützung
- [ ] Erweiterte E-Commerce Integration
- [ ] Voice Responses
- [ ] Performance Optimierungen

### Mittelfristig (3-6 Monate)
- [ ] Smart Home Integration
- [ ] Custom Training Data
- [ ] Advanced Analytics
- [ ] Mobile App

### Langfristig (6+ Monate)
- [ ] Multi-Platform Support
- [ ] Enterprise Features
- [ ] AI Model Fine-tuning
- [ ] Marketplace Integration

## 🆘 Hilfe bekommen

### Erste Schritte
1. Lesen Sie die [README.md](README.md)
2. Schauen Sie in die [Dokumentation](docs/)
3. Durchsuchen Sie [GitHub Issues](https://github.com/your-repo/issues)

### Support
- 📖 [Dokumentation](README.md)
- 🐛 [Bug Report](https://github.com/your-repo/issues/new?template=bug_report.md)
- ✨ [Feature Request](https://github.com/your-repo/issues/new?template=feature_request.md)
- 💬 [Diskussionen](https://github.com/your-repo/discussions)

## 🙏 Anerkennung

Alle Beiträge werden in der [CONTRIBUTORS.md](CONTRIBUTORS.md) gewürdigt.

---

**Vielen Dank, dass Sie JARVIS besser machen! 🤖**
