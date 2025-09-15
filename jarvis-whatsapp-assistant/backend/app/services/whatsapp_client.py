import aiohttp
import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppClient:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for WhatsApp API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, to: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via WhatsApp API"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            **message
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self._get_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Message sent successfully to {to}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"WhatsApp API error: {response.status} - {error_text}")
                        raise Exception(f"WhatsApp API error: {error_text}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message"""
        message = {
            "type": "text",
            "text": {"body": text}
        }
        return await self.send_message(to, message)
    
    async def send_interactive_message(
        self, 
        to: str, 
        header: str, 
        body: str, 
        buttons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send interactive message with buttons"""
        message = {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header},
                "body": {"text": body},
                "action": {
                    "buttons": buttons
                }
            }
        }
        return await self.send_message(to, message)
    
    async def send_template_message(
        self, 
        to: str, 
        template_name: str, 
        language_code: str = "de",
        parameters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send template message"""
        template_components = []
        
        if parameters:
            template_components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": param} for param in parameters]
            })
        
        message = {
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": template_components
            }
        }
        return await self.send_message(to, message)
    
    async def get_media_url(self, media_id: str) -> str:
        """Get media URL from media ID"""
        url = f"{self.base_url}/{media_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["url"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get media URL: {response.status} - {error_text}")
                        raise Exception(f"Failed to get media URL: {error_text}")
        except Exception as e:
            logger.error(f"Error getting media URL: {e}")
            raise
    
    async def download_media(self, media_url: str) -> bytes:
        """Download media content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to download media: {response.status} - {error_text}")
                        raise Exception(f"Failed to download media: {error_text}")
        except Exception as e:
            logger.error(f"Error downloading media: {e}")
            raise
    
    async def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self._get_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Message {message_id} marked as read")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to mark message as read: {response.status} - {error_text}")
                        raise Exception(f"Failed to mark message as read: {error_text}")
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            raise

# Global WhatsApp client instance
whatsapp_client = WhatsAppClient()
