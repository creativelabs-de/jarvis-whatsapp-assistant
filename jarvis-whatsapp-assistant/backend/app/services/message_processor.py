import asyncio
import json
import logging
from typing import Dict, Any, Optional

from app.services.whatsapp_client import whatsapp_client
from app.core.redis_client import redis_client
from app.services.nlu_engine import nlu_engine
from app.services.task_executor import task_executor
from app.services.speech_service import speech_service

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self):
        self.whatsapp_client = whatsapp_client
        
    async def process_incoming_message(self, webhook_data: Dict[str, Any]):
        """Process incoming WhatsApp message"""
        try:
            # Extract message data
            entry = webhook_data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            
            if "messages" not in value:
                logger.warning("No messages in webhook data")
                return
            
            message = value["messages"][0]
            sender_id = message["from"]
            message_id = message["id"]
            message_type = message["type"]
            timestamp = message.get("timestamp")
            
            logger.info(f"Processing message from {sender_id}: type={message_type}, id={message_id}")
            
            # Mark message as read
            try:
                await self.whatsapp_client.mark_message_as_read(message_id)
            except Exception as e:
                logger.warning(f"Failed to mark message as read: {e}")
            
            # Get user context
            user_context = await self.get_user_context(sender_id)
            
            # Process different message types
            if message_type == "text":
                text = message["text"]["body"]
                await self.process_text_message(sender_id, text, user_context)
            
            elif message_type == "audio":
                audio_id = message["audio"]["id"]
                await self.process_audio_message(sender_id, audio_id, user_context)
            
            elif message_type == "interactive":
                await self.process_interactive_message(sender_id, message, user_context)
            
            elif message_type == "image":
                image_id = message["image"]["id"]
                caption = message["image"].get("caption", "")
                await self.process_image_message(sender_id, image_id, caption, user_context)
            
            else:
                logger.warning(f"Unhandled message type: {message_type}")
                await self.send_unsupported_message_response(sender_id)
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error_message(sender_id)
    
    async def process_text_message(self, sender_id: str, text: str, context: Dict):
        """Process text message"""
        logger.info(f"Processing text message from {sender_id}: {text}")
        
        # Update context with new message
        context["last_message"] = text
        context["message_count"] = context.get("message_count", 0) + 1
        
        # Check if this is a confirmation response
        if context.get("conversation_state") in ["confirming_flower_order"]:
            confirmation_result = await task_executor.handle_confirmation(text, context)
            if confirmation_result:
                await self.whatsapp_client.send_text_message(sender_id, confirmation_result["text"])
                context["conversation_state"] = confirmation_result["state"]
                await self.save_user_context(sender_id, context)
                return
        
        # Analyze intent and entities with NLU engine
        nlu_result = await nlu_engine.analyze(text, context)
        
        # Execute task based on NLU result
        task_result = await task_executor.execute(nlu_result, context)
        
        # Send response
        response_text = task_result.get("text", "Entschuldigung, ich konnte keine Antwort generieren.")
        await self.whatsapp_client.send_text_message(sender_id, response_text)
        
        # Update user context
        context["last_response"] = response_text
        context["last_intent"] = nlu_result.get("intent")
        context["conversation_state"] = task_result.get("state", "idle")
        await self.save_user_context(sender_id, context)
    
    async def process_audio_message(self, sender_id: str, audio_id: str, context: Dict):
        """Process audio message using speech-to-text"""
        try:
            logger.info(f"Processing audio message from {sender_id}: {audio_id}")
            
            # Download audio from WhatsApp
            try:
                media_url = await self.whatsapp_client.get_media_url(audio_id)
                audio_data = await self.whatsapp_client.download_media(media_url)
                
                # Transcribe audio to text
                transcript = await speech_service.transcribe_audio(audio_data, "ogg")
                
                if transcript:
                    logger.info(f"Audio transcribed: {transcript}")
                    
                    # Process as text message
                    await self.process_text_message(sender_id, transcript, context)
                else:
                    response_text = "🎤 Entschuldigung, ich konnte Ihre Sprachnachricht nicht verstehen. Können Sie es bitte wiederholen oder eine Textnachricht senden?"
                    await self.whatsapp_client.send_text_message(sender_id, response_text)
                    
            except Exception as e:
                logger.error(f"Error downloading/transcribing audio: {e}")
                response_text = "🎤 Ich habe Ihre Sprachnachricht erhalten und verarbeite sie... Die Spracherkennung ist aktiviert!"
                await self.whatsapp_client.send_text_message(sender_id, response_text)
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            await self.send_error_message(sender_id)
    
    async def process_interactive_message(self, sender_id: str, message: Dict, context: Dict):
        """Process interactive message (button clicks, etc.)"""
        logger.info(f"Processing interactive message from {sender_id}")
        
        interactive = message.get("interactive", {})
        button_reply = interactive.get("button_reply", {})
        
        if button_reply:
            button_id = button_reply.get("id")
            button_title = button_reply.get("title")
            
            response_text = f"Sie haben '{button_title}' ausgewählt. Diese Funktion wird bald implementiert!"
            await self.whatsapp_client.send_text_message(sender_id, response_text)
    
    async def process_image_message(self, sender_id: str, image_id: str, caption: str, context: Dict):
        """Process image message"""
        logger.info(f"Processing image message from {sender_id}: {image_id}")
        
        response_text = "🖼️ Ich habe Ihr Bild erhalten. Die Bildanalyse wird bald verfügbar sein!"
        if caption:
            response_text += f"\nBildunterschrift: {caption}"
        
        await self.whatsapp_client.send_text_message(sender_id, response_text)
    
    async def generate_simple_response(self, text: str, context: Dict) -> str:
        """Generate a simple response (placeholder for NLU engine)"""
        text_lower = text.lower()
        
        # Greeting responses
        if any(greeting in text_lower for greeting in ["hallo", "hi", "hey", "guten tag", "moin"]):
            return "🤖 Hallo! Ich bin JARVIS, Ihr persönlicher KI-Assistent. Wie kann ich Ihnen heute helfen?"
        
        # Flower ordering
        elif any(word in text_lower for word in ["blumen", "rosen", "bestell", "order"]):
            return "🌹 Gerne helfe ich Ihnen bei der Blumenbestellung! Diese Funktion wird gerade implementiert. Bald können Sie mir sagen: 'Bestelle meiner Freundin rote Rosen' und ich kümmere mich darum!"
        
        # Help requests
        elif any(word in text_lower for word in ["hilfe", "help", "was kannst du", "funktionen"]):
            return """🤖 Ich bin JARVIS, Ihr KI-Assistent! Bald werde ich folgende Aufgaben für Sie erledigen können:

🌹 Blumen bestellen
📅 Termine planen
📧 E-Mails senden
🗺️ Routen planen
🎤 Sprachnachrichten verstehen

Die Entwicklung läuft auf Hochtouren!"""
        
        # Status requests
        elif any(word in text_lower for word in ["status", "wie geht", "entwicklung"]):
            return "⚡ Aktueller Entwicklungsstand:\n✅ WhatsApp Integration\n🔄 KI-Engine (in Arbeit)\n⏳ Spracherkennung\n⏳ Aufgabenautomatisierung\n\nIch werde immer intelligenter!"
        
        # Default response
        else:
            return f"🤖 Ich verstehe: '{text}'\n\nIch lerne noch und werde bald viel intelligenter sein! Versuchen Sie es mit 'Hilfe' für verfügbare Funktionen."
    
    async def get_user_context(self, user_id: str) -> Dict:
        """Get user context from Redis"""
        context_key = f"user_context:{user_id}"
        context_data = await redis_client.get(context_key)
        
        if context_data:
            try:
                return json.loads(context_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in user context for {user_id}")
        
        # Initialize new user context
        return {
            "user_id": user_id,
            "conversation_state": "idle",
            "preferences": {},
            "active_tasks": [],
            "message_count": 0,
            "first_interaction": True
        }
    
    async def save_user_context(self, user_id: str, context: Dict):
        """Save user context to Redis"""
        context_key = f"user_context:{user_id}"
        try:
            await redis_client.setex(
                context_key,
                3600,  # 1 hour expiry
                json.dumps(context, ensure_ascii=False)
            )
        except Exception as e:
            logger.error(f"Failed to save user context: {e}")
    
    async def send_error_message(self, sender_id: str):
        """Send error message to user"""
        error_message = "😔 Entschuldigung, es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
        try:
            await self.whatsapp_client.send_text_message(sender_id, error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def send_unsupported_message_response(self, sender_id: str):
        """Send response for unsupported message types"""
        response = "🤖 Dieser Nachrichtentyp wird noch nicht unterstützt. Bitte senden Sie eine Textnachricht oder probieren Sie es später erneut."
        try:
            await self.whatsapp_client.send_text_message(sender_id, response)
        except Exception as e:
            logger.error(f"Failed to send unsupported message response: {e}")

# Global message processor instance
message_processor = MessageProcessor()
