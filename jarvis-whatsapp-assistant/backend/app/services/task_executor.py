import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.ecommerce_service import ecommerce_service

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self):
        self.active_tasks = {}
    
    async def execute(self, nlu_result: Dict[str, Any], context: Dict) -> Dict[str, Any]:
        """Execute task based on NLU result"""
        intent = nlu_result.get("intent")
        entities = nlu_result.get("entities", {})
        user_id = context.get("user_id")
        
        logger.info(f"Executing task for intent: {intent}")
        
        try:
            if intent == "greeting":
                return await self.handle_greeting(nlu_result, context)
            
            elif intent == "order_flowers":
                return await self.handle_flower_order(entities, context, nlu_result)
            
            elif intent == "schedule_meeting":
                return await self.handle_meeting_scheduling(entities, context, nlu_result)
            
            elif intent == "send_email":
                return await self.handle_email_sending(entities, context, nlu_result)
            
            elif intent == "get_weather":
                return await self.handle_weather_request(entities, context, nlu_result)
            
            elif intent == "help":
                return await self.handle_help_request(nlu_result, context)
            
            elif intent == "general_chat":
                return await self.handle_general_chat(nlu_result, context)
            
            elif intent == "goodbye":
                return await self.handle_goodbye(nlu_result, context)
            
            else:
                return await self.handle_unknown_intent(nlu_result, context)
        
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return {
                "type": "text",
                "text": "😔 Es ist ein Fehler bei der Ausführung aufgetreten. Bitte versuchen Sie es erneut.",
                "state": "error"
            }
    
    async def handle_greeting(self, nlu_result: Dict, context: Dict) -> Dict[str, Any]:
        """Handle greeting"""
        is_first_time = context.get("first_interaction", True)
        
        if is_first_time:
            response = """🤖 Hallo! Ich bin JARVIS, Ihr persönlicher KI-Assistent!

Ich kann Ihnen bei folgenden Aufgaben helfen:
🌹 Blumen bestellen
📅 Termine planen
📧 E-Mails senden
🌤️ Wetter abfragen

Probieren Sie es aus: "Bestelle meiner Freundin rote Rosen" """
            context["first_interaction"] = False
        else:
            response = nlu_result.get("response", "Hallo! Wie kann ich Ihnen helfen?")
        
        return {
            "type": "text",
            "text": response,
            "state": "idle"
        }
    
    async def handle_flower_order(self, entities: Dict, context: Dict, nlu_result: Dict) -> Dict[str, Any]:
        """Handle flower ordering process"""
        conversation_state = context.get("conversation_state", "idle")
        user_id = context.get("user_id")
        
        # Get or create order data
        order_key = f"flower_order_{user_id}"
        order_data = context.get("active_order", {})
        
        # Update order data with new entities
        if entities.get("recipient"):
            order_data["recipient"] = entities["recipient"]
        if entities.get("flower_type"):
            order_data["flower_type"] = entities["flower_type"]
        if entities.get("quantity"):
            order_data["quantity"] = entities["quantity"]
        if entities.get("delivery_date"):
            order_data["delivery_date"] = entities["delivery_date"]
        if entities.get("delivery_address"):
            order_data["delivery_address"] = entities["delivery_address"]
        
        # Check what information is still missing
        missing_info = []
        if not order_data.get("recipient"):
            missing_info.append("Empfänger")
        if not order_data.get("flower_type"):
            missing_info.append("Blumenart")
        if not order_data.get("delivery_address"):
            missing_info.append("Lieferadresse")
        
        if missing_info:
            # Still collecting information
            context["active_order"] = order_data
            context["conversation_state"] = "collecting_flower_order"
            
            if len(missing_info) == 3:
                # First time, ask for basic info
                response = """🌹 Gerne helfe ich bei der Blumenbestellung!

Ich benötige folgende Informationen:
• Für wen sind die Blumen? (z.B. "für meine Freundin")
• Welche Blumen? (z.B. "rote Rosen")  
• Lieferadresse?

Sie können alles auf einmal schreiben oder Schritt für Schritt."""
            else:
                response = f"Ich benötige noch: {', '.join(missing_info)}\n\nBitte geben Sie mir diese Information."
            
            return {
                "type": "text", 
                "text": response,
                "state": "collecting_flower_order"
            }
        else:
            # All info collected, confirm order
            return await self.confirm_flower_order(order_data, context)
    
    async def confirm_flower_order(self, order_data: Dict, context: Dict) -> Dict[str, Any]:
        """Confirm flower order with user"""
        # Set default delivery date if not specified
        if not order_data.get("delivery_date"):
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
            order_data["delivery_date"] = tomorrow
        
        confirmation_text = f"""🌹 Bestellbestätigung:

• Blumen: {order_data['flower_type']}
• Empfänger: {order_data['recipient']}
• Lieferadresse: {order_data['delivery_address']}
• Lieferdatum: {order_data['delivery_date']}
• Geschätzte Kosten: 29,99€

Soll ich die Bestellung aufgeben? (Ja/Nein)"""
        
        context["pending_order"] = order_data
        context["conversation_state"] = "confirming_flower_order"
        
        return {
            "type": "text",
            "text": confirmation_text,
            "state": "confirming_flower_order"
        }
    
    async def handle_meeting_scheduling(self, entities: Dict, context: Dict, nlu_result: Dict) -> Dict[str, Any]:
        """Handle meeting scheduling"""
        return {
            "type": "text",
            "text": "📅 Die Terminplanung wird bald verfügbar sein! Ich werde dann Ihre Kalender-Apps integrieren können.",
            "state": "idle"
        }
    
    async def handle_email_sending(self, entities: Dict, context: Dict, nlu_result: Dict) -> Dict[str, Any]:
        """Handle email sending"""
        return {
            "type": "text",
            "text": "📧 Der E-Mail-Versand wird bald verfügbar sein! Ich werde dann E-Mails in Ihrem Namen senden können.",
            "state": "idle"
        }
    
    async def handle_weather_request(self, entities: Dict, context: Dict, nlu_result: Dict) -> Dict[str, Any]:
        """Handle weather requests"""
        location = entities.get("location", "Ihrem Standort")
        return {
            "type": "text",
            "text": f"🌤️ Die Wetterabfrage für {location} wird bald verfügbar sein! Ich werde dann aktuelle Wetterdaten abrufen können.",
            "state": "idle"
        }
    
    async def handle_help_request(self, nlu_result: Dict, context: Dict) -> Dict[str, Any]:
        """Handle help requests"""
        return {
            "type": "text",
            "text": nlu_result.get("response", "Wie kann ich Ihnen helfen?"),
            "state": "idle"
        }
    
    async def handle_general_chat(self, nlu_result: Dict, context: Dict) -> Dict[str, Any]:
        """Handle general conversation"""
        return {
            "type": "text",
            "text": nlu_result.get("response", "Interessant! Wie kann ich Ihnen weiterhelfen?"),
            "state": "idle"
        }
    
    async def handle_goodbye(self, nlu_result: Dict, context: Dict) -> Dict[str, Any]:
        """Handle goodbye"""
        return {
            "type": "text",
            "text": "👋 Auf Wiedersehen! Ich bin jederzeit für Sie da, wenn Sie mich brauchen.",
            "state": "idle"
        }
    
    async def handle_unknown_intent(self, nlu_result: Dict, context: Dict) -> Dict[str, Any]:
        """Handle unknown intents"""
        return {
            "type": "text",
            "text": "🤖 Das habe ich nicht ganz verstanden. Versuchen Sie 'Hilfe' für verfügbare Funktionen oder fragen Sie mich nach Blumen, Terminen oder dem Wetter!",
            "state": "idle"
        }
    
    async def handle_confirmation(self, text: str, context: Dict) -> Dict[str, Any]:
        """Handle yes/no confirmations"""
        text_lower = text.lower()
        
        if context.get("conversation_state") == "confirming_flower_order":
            if any(word in text_lower for word in ["ja", "yes", "ok", "bestellen", "bestätigen"]):
                # Confirm order
                order_data = context.get("pending_order", {})
                return await self.place_flower_order(order_data, context)
            
            elif any(word in text_lower for word in ["nein", "no", "abbrechen", "cancel"]):
                # Cancel order
                context.pop("pending_order", None)
                context.pop("active_order", None)
                context["conversation_state"] = "idle"
                
                return {
                    "type": "text",
                    "text": "❌ Bestellung abgebrochen. Kann ich Ihnen anderweitig helfen?",
                    "state": "idle"
                }
        
        return None
    
    async def place_flower_order(self, order_data: Dict, context: Dict) -> Dict[str, Any]:
        """Place the actual flower order"""
        try:
            # Place order via e-commerce service
            order_result = await ecommerce_service.order_flowers(
                flower_type=order_data.get("flower_type"),
                recipient=order_data.get("recipient"),
                delivery_address=order_data.get("delivery_address"),
                delivery_date=order_data.get("delivery_date"),
                message=order_data.get("message", "Liebe Grüße!")
            )
            
            # Clear order data from context
            context.pop("pending_order", None)
            context.pop("active_order", None)
            context["conversation_state"] = "idle"
            
            if order_result["success"]:
                success_message = f"""✅ Bestellung erfolgreich aufgegeben!

📋 Bestellnummer: {order_result['order_id']}
🌹 Blumen: {order_result['product_name']}
👤 Empfänger: {order_data['recipient']}
📍 Lieferadresse: {order_data['delivery_address']}
📅 Lieferdatum: {order_result['delivery_date']}
💰 Kosten: {order_result['price']:.2f}€

Die Blumen werden zwischen {order_result.get('estimated_delivery_time', '10:00-18:00')} geliefert! 🚚

Tracking: {order_result.get('tracking_url', 'Link folgt per E-Mail')}"""
                
                return {
                    "type": "text",
                    "text": success_message,
                    "state": "idle"
                }
            else:
                error_message = f"❌ Bestellung fehlgeschlagen: {order_result['error']}"
                
                # Add suggestions if available
                if "suggestions" in order_result:
                    suggestions = order_result["suggestions"]
                    suggestion_text = "\n\n🌸 Verfügbare Alternativen:\n"
                    for suggestion in suggestions[:3]:
                        suggestion_text += f"• {suggestion['name']} - {suggestion['price']:.2f}€\n"
                    error_message += suggestion_text
                
                return {
                    "type": "text",
                    "text": error_message,
                    "state": "idle"
                }
        
        except Exception as e:
            logger.error(f"Error placing flower order: {e}")
            return {
                "type": "text",
                "text": "❌ Ein technischer Fehler ist aufgetreten. Bitte versuchen Sie es später erneut oder kontaktieren Sie den Support.",
                "state": "idle"
            }

# Global task executor instance
task_executor = TaskExecutor()
