from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import hmac
import hashlib
import json
import logging
from typing import Dict, Any

from app.core.config import settings
from app.services.message_processor import MessageProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize message processor
message_processor = MessageProcessor()

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"), 
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    """Verify WhatsApp webhook during setup"""
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verification successful")
        return PlainTextResponse(hub_challenge)
    
    logger.error("Webhook verification failed")
    raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    try:
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        # Verify webhook signature (optional but recommended for production)
        if settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN and not verify_signature(body, signature):
            logger.error("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse webhook data
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # Process webhook data
        await process_webhook_data(data)
        
        return {"status": "ok"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    if not signature.startswith("sha256="):
        return False
    
    try:
        expected_signature = hmac.new(
            settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        received_signature = signature[7:]  # Remove "sha256=" prefix
        return hmac.compare_digest(expected_signature, received_signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False

async def process_webhook_data(data: Dict[str, Any]):
    """Process webhook data and route to appropriate handlers"""
    try:
        # Check if this is a message webhook
        if "entry" not in data:
            logger.warning("No 'entry' field in webhook data")
            return
        
        for entry in data["entry"]:
            if "changes" not in entry:
                continue
                
            for change in entry["changes"]:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    
                    # Handle incoming messages
                    if "messages" in value:
                        await message_processor.process_incoming_message(data)
                    
                    # Handle message status updates
                    elif "statuses" in value:
                        await handle_message_status(value["statuses"])
                    
                    # Handle other webhook events
                    else:
                        logger.info(f"Unhandled webhook event: {change}")
    
    except Exception as e:
        logger.error(f"Error processing webhook data: {e}")
        raise

async def handle_message_status(statuses: list):
    """Handle message status updates (delivered, read, etc.)"""
    for status in statuses:
        message_id = status.get("id")
        status_type = status.get("status")
        timestamp = status.get("timestamp")
        
        logger.info(f"Message {message_id} status: {status_type} at {timestamp}")
        
        # Here you could update message status in database
        # For now, just log the status update
