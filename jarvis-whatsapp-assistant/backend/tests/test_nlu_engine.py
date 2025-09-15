import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.services.nlu_engine import NLUEngine

class TestNLUEngine:
    
    def setup_method(self):
        """Setup for each test"""
        self.nlu_engine = NLUEngine()
    
    @pytest.mark.asyncio
    async def test_greeting_intent(self):
        """Test greeting intent recognition"""
        context = {"user_id": "test_user"}
        
        result = await self.nlu_engine.analyze("Hallo JARVIS", context)
        
        assert result["intent"] == "greeting"
        assert result["confidence"] > 0.9
        assert "Hallo" in result["response"]
    
    @pytest.mark.asyncio
    async def test_flower_order_intent(self):
        """Test flower ordering intent"""
        context = {"user_id": "test_user"}
        
        result = await self.nlu_engine.analyze("Bestelle meiner Freundin rote Rosen", context)
        
        assert result["intent"] == "order_flowers"
        assert result["entities"]["recipient"] == "Freundin"
        assert result["entities"]["flower_type"] == "rote Rosen"
        assert result["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_help_intent(self):
        """Test help intent recognition"""
        context = {"user_id": "test_user"}
        
        result = await self.nlu_engine.analyze("Hilfe", context)
        
        assert result["intent"] == "help"
        assert result["confidence"] > 0.9
        assert "helfen" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_general_chat_intent(self):
        """Test general chat intent"""
        context = {"user_id": "test_user"}
        
        result = await self.nlu_engine.analyze("Wie geht es dir?", context)
        
        assert result["intent"] == "general_chat"
        assert result["confidence"] > 0.5
    
    def test_extract_recipient(self):
        """Test recipient extraction"""
        assert self.nlu_engine._extract_recipient("für meine Freundin") == "Freundin"
        assert self.nlu_engine._extract_recipient("meinem Freund") == "Freund"
        assert self.nlu_engine._extract_recipient("meiner Mutter") == "Mutter"
        assert self.nlu_engine._extract_recipient("random text") is None
    
    def test_extract_flower_type(self):
        """Test flower type extraction"""
        assert self.nlu_engine._extract_flower_type("rote Rosen") == "rote Rosen"
        assert self.nlu_engine._extract_flower_type("weiße Rosen") == "weiße Rosen"
        assert self.nlu_engine._extract_flower_type("Tulpen") == "Tulpen"
        assert self.nlu_engine._extract_flower_type("random text") is None
    
    @pytest.mark.asyncio
    @patch('openai.ChatCompletion.acreate')
    async def test_openai_integration(self, mock_openai):
        """Test OpenAI integration when available"""
        # Mock OpenAI response
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = json.dumps({
            "intent": "greeting",
            "entities": {},
            "confidence": 0.95,
            "response": "Hello! I'm JARVIS.",
            "action": "greet_user",
            "next_step": "await_user_request"
        })
        mock_openai.return_value = mock_response
        
        # Create engine with OpenAI available
        engine = NLUEngine()
        engine.openai_available = True
        
        context = {"user_id": "test_user"}
        result = await engine.analyze("Hello", context)
        
        assert result["intent"] == "greeting"
        assert result["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_fallback_analyze(self):
        """Test fallback analysis when OpenAI fails"""
        context = {"user_id": "test_user"}
        
        result = await self.nlu_engine._fallback_analyze("test message", context)
        
        assert result["intent"] == "error"
        assert result["confidence"] == 0.0
        assert "technisches Problem" in result["response"]
