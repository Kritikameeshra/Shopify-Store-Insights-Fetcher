#!/usr/bin/env python3
"""
Product Extractor for Shopify Store Insights Fetcher

Developer: Kritika Kumari Mishra
Description: Extracts product catalog and hero products from Shopify stores.
"""

import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ProductExtractor:
    """Class to extract product information from Shopify stores"""
    
    def extract_products(self, products_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract products from Shopify products.json response
        
        Args:
            products_data: JSON response from /products.json endpoint
            
        Returns:
            List of product dictionaries
        """
        try:
            products = []
            if 'products' in products_data:
                for product in products_data['products']:
                    product_info = {
                        'id': product.get('id'),
                        'title': product.get('title'),
                        'handle': product.get('handle'),
                        'description': product.get('body_html'),
                        'vendor': product.get('vendor'),
                        'product_type': product.get('product_type'),
                        'tags': product.get('tags', []),
                        'published_at': product.get('published_at'),
                        'created_at': product.get('created_at'),
                        'updated_at': product.get('updated_at'),
                        'variants': [],
                        'images': [],
                        'options': []
                    }
                    
                    # Extract variants
                    if 'variants' in product:
                        for variant in product['variants']:
                            variant_info = {
                                'id': variant.get('id'),
                                'title': variant.get('title'),
                                'price': variant.get('price'),
                                'compare_at_price': variant.get('compare_at_price'),
                                'sku': variant.get('sku'),
                                'barcode': variant.get('barcode'),
                                'weight': variant.get('weight'),
                                'weight_unit': variant.get('weight_unit'),
                                'inventory_quantity': variant.get('inventory_quantity'),
                                'inventory_management': variant.get('inventory_management'),
                                'available': variant.get('available', False)
                            }
                            product_info['variants'].append(variant_info)
                    
                    # Extract images
                    if 'images' in product:
                        for image in product['images']:
                            image_info = {
                                'id': image.get('id'),
                                'src': image.get('src'),
                                'alt': image.get('alt'),
                                'width': image.get('width'),
                                'height': image.get('height'),
                                'position': image.get('position')
                            }
                            product_info['images'].append(image_info)
                    
                    # Extract options
                    if 'options' in product:
                        for option in product['options']:
                            option_info = {
                                'id': option.get('id'),
                                'name': option.get('name'),
                                'position': option.get('position'),
                                'values': option.get('values', [])
                            }
                            product_info['options'].append(option_info)
                    
                    products.append(product_info)
            
            return products
        except Exception as e:
            logger.error(f"Error extracting products: {str(e)}")
            return []
    
    def extract_hero_products(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract hero products from homepage HTML
        
        Args:
            html: Homepage HTML content
            
        Returns:
            List of hero product dictionaries
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            hero_products = []
            
            # Common selectors for hero products
            selectors = [
                '[class*="hero"] [class*="product"]',
                '[class*="featured"] [class*="product"]',
                '[class*="banner"] [class*="product"]',
                '[class*="slider"] [class*="product"]',
                '[class*="carousel"] [class*="product"]',
                '.product-item',
                '.product-card',
                '.product-tile',
                '[data-product-id]',
                '[data-product-handle]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    product_info = self._extract_product_from_element(element)
                    if product_info and product_info not in hero_products:
                        hero_products.append(product_info)
            
            # Also look for product links in navigation or featured sections
            product_links = soup.find_all('a', href=re.compile(r'/products/'))
            for link in product_links[:10]:  # Limit to first 10
                product_info = self._extract_product_from_link(link)
                if product_info and product_info not in hero_products:
                    hero_products.append(product_info)
            
            return hero_products[:20]  # Limit to 20 hero products
            
        except Exception as e:
            logger.error(f"Error extracting hero products: {str(e)}")
            return []
    
    def _extract_product_from_element(self, element) -> Dict[str, Any]:
        """Extract product information from a DOM element"""
        try:
            product_info = {
                'title': None,
                'price': None,
                'image': None,
                'url': None,
                'description': None
            }
            
            # Extract title
            title_selectors = [
                '[class*="title"]',
                '[class*="name"]',
                'h1', 'h2', 'h3', 'h4',
                '.product-title',
                '.product-name'
            ]
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    product_info['title'] = title_elem.get_text(strip=True)
                    break
            
            # Extract price
            price_selectors = [
                '[class*="price"]',
                '.price',
                '.product-price',
                '[data-price]'
            ]
            
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract price using regex
                    price_match = re.search(r'[\$₹€£]?\s*[\d,]+\.?\d*', price_text)
                    if price_match:
                        product_info['price'] = price_match.group()
                    break
            
            # Extract image
            img_elem = element.find('img')
            if img_elem:
                product_info['image'] = img_elem.get('src') or img_elem.get('data-src')
            
            # Extract URL
            link_elem = element.find('a')
            if link_elem:
                product_info['url'] = link_elem.get('href')
            
            # Extract description
            desc_selectors = [
                '[class*="description"]',
                '[class*="summary"]',
                'p'
            ]
            
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if len(desc_text) > 10:  # Minimum meaningful length
                        product_info['description'] = desc_text
                        break
            
            # Only return if we have at least a title or URL
            if product_info['title'] or product_info['url']:
                return product_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting product from element: {str(e)}")
            return None
    
    def _extract_product_from_link(self, link) -> Dict[str, Any]:
        """Extract product information from a product link"""
        try:
            product_info = {
                'title': None,
                'price': None,
                'image': None,
                'url': link.get('href'),
                'description': None
            }
            
            # Extract title from link text or alt text
            if link.get_text(strip=True):
                product_info['title'] = link.get_text(strip=True)
            
            # Look for image in the link
            img_elem = link.find('img')
            if img_elem:
                product_info['image'] = img_elem.get('src') or img_elem.get('data-src')
                if img_elem.get('alt'):
                    product_info['title'] = product_info['title'] or img_elem.get('alt')
            
            # Extract price from nearby elements
            parent = link.parent
            if parent:
                price_elem = parent.find(text=re.compile(r'[\$₹€£]?\s*[\d,]+\.?\d*'))
                if price_elem:
                    product_info['price'] = price_elem.strip()
            
            return product_info if product_info['title'] or product_info['url'] else None
            
        except Exception as e:
            logger.error(f"Error extracting product from link: {str(e)}")
            return None
