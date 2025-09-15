import openai
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class NLUEngine:
    def __init__(self):
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-demo-key-replace-with-real-key":
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_available = True
        else:
            self.openai_available = False
            logger.warning("OpenAI API key not configured - using mock responses")
    
    async def analyze(self, text: str, context: Dict) -> Dict[str, Any]:
        """Analyze user intent and extract entities"""
        
        if not self.openai_available:
            return await self._mock_analyze(text, context)
        
        try:
            system_prompt = self._get_system_prompt()
            user_prompt = self._get_user_prompt(text, context)
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                timeout=30
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            logger.info(f"NLU analysis result: {result}")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return await self._fallback_analyze(text, context)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return await self._fallback_analyze(text, context)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for OpenAI"""
        return """Du bist JARVIS, ein intelligenter KI-Assistent wie aus Iron Man. Du hilfst Benutzern bei verschiedenen Aufgaben.

Analysiere die Benutzeranfrage und bestimme:
1. Intent (Absicht): Die Hauptabsicht des Benutzers
2. Entities (Entitäten): Relevante Informationen wie Namen, Daten, Orte, Produkte
3. Confidence (Vertrauen): Wie sicher bist du bei der Intent-Erkennung (0.0-1.0)
4. Response (Antwort): Eine natürliche, hilfreiche Antwort für den Benutzer
5. Action (Aktion): Welche Aktion soll ausgeführt werden
6. Next_step: Was ist der nächste Schritt im Prozess

Verfügbare Intents:
- greeting: Begrüßung
- order_flowers: Blumen bestellen
- schedule_meeting: Termin planen
- send_email: E-Mail senden
- get_weather: Wetter abfragen
- general_chat: Allgemeine Unterhaltung
- help: Hilfe anfordern
- goodbye: Verabschiedung

Antworte IMMER im JSON-Format. Sei freundlich und hilfsbereit wie JARVIS."""
    
    def _get_user_prompt(self, text: str, context: Dict) -> str:
        """Get user prompt for OpenAI"""
        return f"""
Benutzeranfrage: "{text}"
Kontext: {json.dumps(context, ensure_ascii=False)}

Beispiel für Blumenbestellung:
Benutzer: "Bestelle meiner Freundin rote Rosen"
{{
    "intent": "order_flowers",
    "entities": {{
        "recipient": "Freundin",
        "flower_type": "rote Rosen",
        "quantity": null,
        "delivery_date": null,
        "delivery_address": null
    }},
    "confidence": 0.95,
    "response": "Gerne bestelle ich rote Rosen für Ihre Freundin! Ich benötige noch die Lieferadresse und ein gewünschtes Lieferdatum. Können Sie mir diese Informationen geben?",
    "action": "collect_order_details",
    "next_step": "ask_delivery_address"
}}

Beispiel für Begrüßung:
Benutzer: "Hallo JARVIS"
{{
    "intent": "greeting",
    "entities": {{}},
    "confidence": 0.98,
    "response": "Hallo! Ich bin JARVIS, Ihr persönlicher KI-Assistent. Wie kann ich Ihnen heute helfen? Ich kann Blumen bestellen, Termine planen, E-Mails senden und vieles mehr!",
    "action": "greet_user",
    "next_step": "await_user_request"
}}

Analysiere jetzt die Benutzeranfrage:
"""
    
    async def _mock_analyze(self, text: str, context: Dict) -> Dict[str, Any]:
        """Mock analysis when OpenAI is not available"""
        text_lower = text.lower()
        
        # Greeting
        if any(greeting in text_lower for greeting in ["hallo", "hi", "hey", "guten tag", "moin"]):
            return {
                "intent": "greeting",
                "entities": {},
                "confidence": 0.95,
                "response": "🤖 Hallo! Ich bin JARVIS, Ihr persönlicher KI-Assistent. Wie kann ich Ihnen heute helfen?",
                "action": "greet_user",
                "next_step": "await_user_request"
            }
        
        # Flower ordering
        elif any(word in text_lower for word in ["blumen", "rosen", "bestell", "order"]):
            return {
                "intent": "order_flowers",
                "entities": {
                    "recipient": self._extract_recipient(text),
                    "flower_type": self._extract_flower_type(text),
                    "quantity": None,
                    "delivery_date": None,
                    "delivery_address": None
                },
                "confidence": 0.85,
                "response": "🌹 Gerne helfe ich Ihnen bei der Blumenbestellung! Ich benötige noch einige Details wie die Lieferadresse und das gewünschte Lieferdatum.",
                "action": "collect_order_details",
                "next_step": "ask_delivery_address"
            }
        
        # Help
        elif any(word in text_lower for word in ["hilfe", "help", "was kannst du", "funktionen"]):
            return {
                "intent": "help",
                "entities": {},
                "confidence": 0.98,
                "response": """🤖 Ich bin JARVIS und kann Ihnen bei folgenden Aufgaben helfen:

🌹 Blumen bestellen
📅 Termine planen  
📧 E-Mails senden
🌤️ Wetter abfragen
💬 Allgemeine Fragen beantworten

Probieren Sie es aus: "Bestelle meiner Freundin rote Rosen" """,
                "action": "show_help",
                "next_step": "await_user_request"
            }
        
        # Default
        else:
            return {
                "intent": "general_chat",
                "entities": {},
                "confidence": 0.6,
                "response": f"🤖 Ich verstehe: '{text}'\n\nIch bin noch im Lernmodus. Versuchen Sie 'Hilfe' für verfügbare Funktionen oder fragen Sie mich nach Blumen, Terminen oder dem Wetter!",
                "action": "general_response",
                "next_step": "await_user_request"
            }
    
    async def _fallback_analyze(self, text: str, context: Dict) -> Dict[str, Any]:
        """Fallback analysis when OpenAI fails"""
        return {
            "intent": "error",
            "entities": {},
            "confidence": 0.0,
            "response": "🤖 Entschuldigung, ich hatte ein kleines technisches Problem. Können Sie Ihre Anfrage bitte wiederholen?",
            "action": "error_recovery",
            "next_step": "await_user_request"
        }
    
    def _extract_recipient(self, text: str) -> Optional[str]:
        """Extract recipient from text"""
        text_lower = text.lower()
        if "freundin" in text_lower:
            return "Freundin"
        elif "freund" in text_lower:
            return "Freund"
        elif "mutter" in text_lower or "mama" in text_lower:
            return "Mutter"
        elif "vater" in text_lower or "papa" in text_lower:
            return "Vater"
        return None
    
    def _extract_flower_type(self, text: str) -> Optional[str]:
        """Extract flower type from text"""
        text_lower = text.lower()
        if "rosen" in text_lower or "rose" in text_lower:
            if "rot" in text_lower:
                return "rote Rosen"
            elif "weiß" in text_lower:
                return "weiße Rosen"
            else:
                return "Rosen"
        elif "tulpen" in text_lower:
            return "Tulpen"
        elif "sonnenblumen" in text_lower:
            return "Sonnenblumen"
        return None

# Global NLU engine instance
nlu_engine = NLUEngine()
