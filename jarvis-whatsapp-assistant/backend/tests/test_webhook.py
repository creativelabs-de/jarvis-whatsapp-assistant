import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)

class TestWebhook:
    
    def test_webhook_verification(self):
        """Test webhook verification endpoint"""
        response = client.get(
            "/api/v1/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "jarvis_webhook_verify_token_2024"
            }
        )
        assert response.status_code == 200
        assert response.text == "test_challenge"
    
    def test_webhook_verification_invalid_token(self):
        """Test webhook verification with invalid token"""
        response = client.get(
            "/api/v1/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "invalid_token"
            }
        )
        assert response.status_code == 403
    
    @patch('app.services.message_processor.message_processor.process_incoming_message')
    def test_webhook_message_processing(self, mock_process):
        """Test webhook message processing"""
        mock_process.return_value = AsyncMock()
        
        webhook_data = {
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
        }
        
        response = client.post(
            "/api/v1/webhook",
            json=webhook_data
        )
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_webhook_invalid_json(self):
        """Test webhook with invalid JSON"""
        response = client.post(
            "/api/v1/webhook",
            data="invalid json"
        )
        assert response.status_code == 400
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "redis" in data
        assert "openai_configured" in data
        assert "whatsapp_configured" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "JARVIS WhatsApp Assistant API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
