import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
from app.core.config import settings

logger = logging.getLogger(__name__)

class ECommerceService:
    def __init__(self):
        self.shopify_api_key = settings.SHOPIFY_API_KEY
        self.shopify_api_secret = settings.SHOPIFY_API_SECRET
        self.shopify_shop_name = settings.SHOPIFY_SHOP_NAME
        
        # Mock product catalog
        self.product_catalog = [
            {
                "id": "1",
                "name": "Rote Rosen Bouquet",
                "price": 29.99,
                "description": "12 frische rote Rosen mit grünem Beiwerk",
                "category": "rosen",
                "keywords": ["rote rosen", "rosen", "rot"],
                "image_url": "https://example.com/red-roses.jpg",
                "available": True
            },
            {
                "id": "2",
                "name": "Weiße Rosen Bouquet", 
                "price": 32.99,
                "description": "12 elegante weiße Rosen",
                "category": "rosen",
                "keywords": ["weiße rosen", "rosen", "weiß"],
                "image_url": "https://example.com/white-roses.jpg",
                "available": True
            },
            {
                "id": "3",
                "name": "Gemischter Blumenstrauß",
                "price": 24.99,
                "description": "Bunter Mix aus Saisonblumen",
                "category": "gemischt",
                "keywords": ["gemischt", "bunt", "saisonblumen"],
                "image_url": "https://example.com/mixed-flowers.jpg",
                "available": True
            },
            {
                "id": "4",
                "name": "Tulpen Bouquet",
                "price": 19.99,
                "description": "10 bunte Tulpen",
                "category": "tulpen",
                "keywords": ["tulpen", "bunt"],
                "image_url": "https://example.com/tulips.jpg",
                "available": True
            },
            {
                "id": "5",
                "name": "Sonnenblumen Strauß",
                "price": 22.99,
                "description": "5 große Sonnenblumen",
                "category": "sonnenblumen",
                "keywords": ["sonnenblumen", "gelb"],
                "image_url": "https://example.com/sunflowers.jpg",
                "available": True
            }
        ]
    
    async def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for products based on query"""
        query_lower = query.lower() if query else ""
        results = []
        
        for product in self.product_catalog:
            if not product["available"]:
                continue
                
            # Check category match
            if category and product["category"] != category.lower():
                continue
            
            # Check keyword match
            if query_lower:
                matches = any(keyword in query_lower for keyword in product["keywords"])
                if matches:
                    results.append(product)
            else:
                results.append(product)
        
        # Sort by relevance (simple scoring)
        if query_lower:
            def score_product(product):
                score = 0
                for keyword in product["keywords"]:
                    if keyword in query_lower:
                        score += len(keyword)
                return score
            
            results.sort(key=score_product, reverse=True)
        
        return results
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        for product in self.product_catalog:
            if product["id"] == product_id:
                return product
        return None
    
    async def order_flowers(
        self,
        flower_type: str,
        recipient: str,
        delivery_address: str,
        delivery_date: Optional[str] = None,
        message: Optional[str] = None,
        quantity: Optional[int] = None
    ) -> Dict[str, Any]:
        """Order flowers through e-commerce platform"""
        
        try:
            logger.info(f"Processing flower order: {flower_type} for {recipient}")
            
            # Search for matching products
            products = await self.search_products(flower_type)
            
            if not products:
                return {
                    "success": False,
                    "error": f"Keine Blumen vom Typ '{flower_type}' gefunden.",
                    "suggestions": await self.get_popular_products()
                }
            
            # Select best matching product
            selected_product = products[0]
            
            # Calculate delivery date
            if not delivery_date:
                delivery_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
            
            # Create order
            order_data = {
                "product_id": selected_product["id"],
                "product_name": selected_product["name"],
                "price": selected_product["price"],
                "quantity": quantity or 1,
                "recipient": recipient,
                "delivery_address": delivery_address,
                "delivery_date": delivery_date,
                "special_message": message or f"Liebe Grüße!",
                "order_timestamp": datetime.now().isoformat()
            }
            
            # Place order
            order_result = await self.place_order(order_data)
            
            if order_result["success"]:
                return {
                    "success": True,
                    "order_id": order_result["order_id"],
                    "product_name": selected_product["name"],
                    "price": selected_product["price"],
                    "delivery_date": delivery_date,
                    "estimated_delivery_time": "10:00 - 18:00",
                    "tracking_url": f"https://example.com/track/{order_result['order_id']}"
                }
            else:
                return {
                    "success": False,
                    "error": order_result.get("error", "Unbekannter Fehler bei der Bestellung")
                }
        
        except Exception as e:
            logger.error(f"Error ordering flowers: {e}")
            return {
                "success": False,
                "error": "Ein technischer Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."
            }
    
    async def place_order(self, order_data: Dict) -> Dict[str, Any]:
        """Place order with e-commerce platform"""
        try:
            # Generate order ID
            order_id = f"FL-{uuid.uuid4().hex[:8].upper()}"
            
            # In a real implementation, this would call Shopify/WooCommerce API
            if self.shopify_api_key and self.shopify_shop_name:
                return await self._place_shopify_order(order_data, order_id)
            else:
                # Mock implementation for demo
                return await self._place_mock_order(order_data, order_id)
        
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _place_shopify_order(self, order_data: Dict, order_id: str) -> Dict[str, Any]:
        """Place order via Shopify API"""
        shopify_url = f"https://{self.shopify_shop_name}.myshopify.com/admin/api/2023-10/orders.json"
        
        headers = {
            "X-Shopify-Access-Token": self.shopify_api_key,
            "Content-Type": "application/json"
        }
        
        order_payload = {
            "order": {
                "line_items": [{
                    "title": order_data["product_name"],
                    "price": order_data["price"],
                    "quantity": order_data.get("quantity", 1)
                }],
                "shipping_address": {
                    "address1": order_data["delivery_address"],
                    "city": "Unknown",
                    "country": "DE"
                },
                "note": order_data.get("special_message", ""),
                "tags": f"jarvis-order,recipient:{order_data['recipient']}"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(shopify_url, json=order_payload, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            "success": True,
                            "order_id": str(result["order"]["id"]),
                            "shopify_order_id": result["order"]["id"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Shopify API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"Shopify API error: {response.status}"
                        }
        except Exception as e:
            logger.error(f"Shopify API exception: {e}")
            return {
                "success": False,
                "error": "Verbindung zu Shopify fehlgeschlagen"
            }
    
    async def _place_mock_order(self, order_data: Dict, order_id: str) -> Dict[str, Any]:
        """Mock order placement for demo"""
        # Simulate processing time
        import asyncio
        await asyncio.sleep(0.1)
        
        # Simulate 95% success rate
        import random
        if random.random() < 0.95:
            logger.info(f"Mock order placed successfully: {order_id}")
            return {
                "success": True,
                "order_id": order_id
            }
        else:
            return {
                "success": False,
                "error": "Temporärer Fehler beim Zahlungsanbieter"
            }
    
    async def get_popular_products(self) -> List[Dict[str, Any]]:
        """Get list of popular products"""
        return [
            {"name": "Rote Rosen", "price": 29.99},
            {"name": "Gemischter Strauß", "price": 24.99},
            {"name": "Tulpen", "price": 19.99}
        ]
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        # Mock implementation
        return {
            "order_id": order_id,
            "status": "confirmed",
            "estimated_delivery": "Morgen zwischen 10:00-18:00",
            "tracking_number": f"TRK{order_id[-6:]}"
        }
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order"""
        # Mock implementation
        return {
            "success": True,
            "message": f"Bestellung {order_id} wurde storniert",
            "refund_amount": 29.99
        }

# Global e-commerce service instance
ecommerce_service = ECommerceService()
