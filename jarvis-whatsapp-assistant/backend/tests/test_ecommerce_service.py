import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.services.ecommerce_service import ECommerceService

class TestECommerceService:
    
    def setup_method(self):
        """Setup for each test"""
        self.ecommerce_service = ECommerceService()
    
    @pytest.mark.asyncio
    async def test_search_products(self):
        """Test product search functionality"""
        results = await self.ecommerce_service.search_products("rote Rosen")
        
        assert len(results) > 0
        assert any("rote rosen" in product["keywords"] for product in results)
        assert all(product["available"] for product in results)
    
    @pytest.mark.asyncio
    async def test_search_products_by_category(self):
        """Test product search by category"""
        results = await self.ecommerce_service.search_products("", category="rosen")
        
        assert len(results) > 0
        assert all(product["category"] == "rosen" for product in results)
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self):
        """Test getting product by ID"""
        product = await self.ecommerce_service.get_product_by_id("1")
        
        assert product is not None
        assert product["id"] == "1"
        assert product["name"] == "Rote Rosen Bouquet"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_product(self):
        """Test getting non-existent product"""
        product = await self.ecommerce_service.get_product_by_id("999")
        
        assert product is None
    
    @pytest.mark.asyncio
    async def test_order_flowers_success(self):
        """Test successful flower ordering"""
        result = await self.ecommerce_service.order_flowers(
            flower_type="rote Rosen",
            recipient="Freundin",
            delivery_address="Musterstraße 1, 12345 Berlin",
            delivery_date="25.12.2024"
        )
        
        assert result["success"] is True
        assert "order_id" in result
        assert result["product_name"] == "Rote Rosen Bouquet"
        assert result["price"] == 29.99
    
    @pytest.mark.asyncio
    async def test_order_flowers_not_found(self):
        """Test ordering non-existent flowers"""
        result = await self.ecommerce_service.order_flowers(
            flower_type="nicht existierende Blumen",
            recipient="Freundin",
            delivery_address="Musterstraße 1, 12345 Berlin"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "suggestions" in result
    
    @pytest.mark.asyncio
    async def test_place_mock_order(self):
        """Test mock order placement"""
        order_data = {
            "product_name": "Test Flowers",
            "price": 25.99,
            "recipient": "Test Recipient",
            "delivery_address": "Test Address"
        }
        
        result = await self.ecommerce_service._place_mock_order(order_data, "TEST123")
        
        assert "success" in result
        if result["success"]:
            assert result["order_id"] == "TEST123"
    
    @pytest.mark.asyncio
    async def test_get_popular_products(self):
        """Test getting popular products"""
        products = await self.ecommerce_service.get_popular_products()
        
        assert len(products) > 0
        assert all("name" in product and "price" in product for product in products)
    
    @pytest.mark.asyncio
    async def test_get_order_status(self):
        """Test order status retrieval"""
        status = await self.ecommerce_service.get_order_status("TEST123")
        
        assert "order_id" in status
        assert "status" in status
        assert status["order_id"] == "TEST123"
    
    @pytest.mark.asyncio
    async def test_cancel_order(self):
        """Test order cancellation"""
        result = await self.ecommerce_service.cancel_order("TEST123")
        
        assert result["success"] is True
        assert "message" in result
        assert "refund_amount" in result
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_shopify_integration(self, mock_post):
        """Test Shopify API integration"""
        # Mock successful Shopify response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = {
            "order": {"id": 12345}
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Create service with Shopify credentials
        service = ECommerceService()
        service.shopify_api_key = "test_key"
        service.shopify_shop_name = "test_shop"
        
        order_data = {
            "product_name": "Test Flowers",
            "price": 25.99,
            "recipient": "Test Recipient",
            "delivery_address": "Test Address",
            "special_message": "Test message"
        }
        
        result = await service._place_shopify_order(order_data, "TEST123")
        
        assert result["success"] is True
        assert result["shopify_order_id"] == 12345
