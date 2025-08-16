#!/usr/bin/env python3
"""
Shopify Store Insights Fetcher - Main Orchestrator

Developer: Kritika Kumari Mishra
Description: Main class that coordinates all data extraction tasks from Shopify stores.
"""

import aiohttp
import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
from product_extractor import ProductExtractor
from policy_extractor import PolicyExtractor
from faq_extractor import FAQExtractor
from contact_extractor import ContactExtractor
from social_extractor import SocialExtractor
from llm_processor import GeminiProcessor

logger = logging.getLogger(__name__)

@dataclass
class BrandInsights:
    """Data class to hold all brand insights"""
    store_url: str
    products: List[Dict[str, Any]]
    hero_products: List[Dict[str, Any]]
    privacy_policy: Optional[str]
    return_refund_policy: Optional[str]
    faqs: List[Dict[str, str]]
    social_handles: Dict[str, str]
    contact_details: Dict[str, str]
    brand_context: Optional[str]
    important_links: Dict[str, str]
    metadata: Dict[str, Any]

class ShopifyInsightsFetcher:
    """Main class for fetching insights from Shopify stores"""
    
    def __init__(self):
        self.session = None
        self.base_url = None
        self.product_extractor = ProductExtractor()
        self.policy_extractor = PolicyExtractor()
        self.faq_extractor = FAQExtractor()
        self.contact_extractor = ContactExtractor()
        self.social_extractor = SocialExtractor()
        self.llm_processor = GeminiProcessor()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_store_insights(self, website_url: str) -> Dict[str, Any]:
        """
        Main method to fetch all insights from a Shopify store
        
        Args:
            website_url: The Shopify store URL
            
        Returns:
            Dictionary containing all brand insights
        """
        async with self:
            self.base_url = website_url.rstrip('/')
            
            try:
                # Fetch all insights concurrently
                tasks = [
                    self._fetch_products(),
                    self._fetch_hero_products(),
                    self._fetch_policies(),
                    self._fetch_faqs(),
                    self._fetch_social_handles(),
                    self._fetch_contact_details(),
                    self._fetch_brand_context(),
                    self._fetch_important_links(),
                    self._fetch_metadata()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Create insights object
                insights = BrandInsights(
                    store_url=self.base_url,
                    products=results[0] if not isinstance(results[0], Exception) else [],
                    hero_products=results[1] if not isinstance(results[1], Exception) else [],
                    privacy_policy=results[2].get('privacy') if not isinstance(results[2], Exception) else None,
                    return_refund_policy=results[2].get('return_refund') if not isinstance(results[2], Exception) else None,
                    faqs=results[3] if not isinstance(results[3], Exception) else [],
                    social_handles=results[4] if not isinstance(results[4], Exception) else {},
                    contact_details=results[5] if not isinstance(results[5], Exception) else {},
                    brand_context=results[6] if not isinstance(results[6], Exception) else None,
                    important_links=results[7] if not isinstance(results[7], Exception) else {},
                    metadata=results[8] if not isinstance(results[8], Exception) else {}
                )
                
                # Convert to dict for LLM processing
                insights_dict = self._to_dict(insights)
                
                # Enhance with LLM processing
                try:
                    # Get HTML content for brand context enhancement
                    async with self.session.get(self.base_url) as response:
                        html_content = await response.text() if response.status == 200 else ""
                    
                    # Process with LLM
                    enhanced_faqs = await self.llm_processor.structure_faqs(insights_dict.get('faqs', []))
                    enhanced_brand_context = await self.llm_processor.extract_brand_context(
                        html_content, insights_dict.get('metadata', {})
                    )
                    product_analysis = await self.llm_processor.categorize_products(insights_dict.get('products', []))
                    social_analysis = await self.llm_processor.enhance_social_analysis(insights_dict.get('social_handles', {}))
                    insights_summary = await self.llm_processor.generate_insights_summary(insights_dict)
                    
                    # Update insights with enhanced data
                    insights_dict.update({
                        'faqs': enhanced_faqs,
                        'brand_context': enhanced_brand_context,
                        'product_analysis': product_analysis,
                        'social_analysis': social_analysis,
                        'insights_summary': insights_summary
                    })
                    
                    # Validate and clean data
                    insights_dict = await self.llm_processor.validate_and_clean_data(insights_dict)
                    
                except Exception as e:
                    logger.warning(f"LLM processing failed, using original data: {str(e)}")
                
                return insights_dict
                
            except Exception as e:
                logger.error(f"Error fetching store insights: {str(e)}")
                raise
    
    async def _fetch_products(self) -> List[Dict[str, Any]]:
        """Fetch all products from the store"""
        try:
            products_url = f"{self.base_url}/products.json"
            async with self.session.get(products_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.product_extractor.extract_products(data)
                else:
                    logger.warning(f"Failed to fetch products: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            return []
    
    async def _fetch_hero_products(self) -> List[Dict[str, Any]]:
        """Fetch hero products from homepage"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.product_extractor.extract_hero_products(html)
                else:
                    logger.warning(f"Failed to fetch homepage: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching hero products: {str(e)}")
            return []
    
    async def _fetch_policies(self) -> Dict[str, str]:
        """Fetch privacy and return/refund policies"""
        try:
            return await self.policy_extractor.extract_policies(self.session, self.base_url)
        except Exception as e:
            logger.error(f"Error fetching policies: {str(e)}")
            return {}
    
    async def _fetch_faqs(self) -> List[Dict[str, str]]:
        """Fetch FAQs from the store"""
        try:
            return await self.faq_extractor.extract_faqs(self.session, self.base_url)
        except Exception as e:
            logger.error(f"Error fetching FAQs: {str(e)}")
            return []
    
    async def _fetch_social_handles(self) -> Dict[str, str]:
        """Fetch social media handles"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.social_extractor.extract_social_handles(html)
                else:
                    logger.warning(f"Failed to fetch homepage for social handles: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching social handles: {str(e)}")
            return {}
    
    async def _fetch_contact_details(self) -> Dict[str, str]:
        """Fetch contact details"""
        try:
            return await self.contact_extractor.extract_contact_details(self.session, self.base_url)
        except Exception as e:
            logger.error(f"Error fetching contact details: {str(e)}")
            return {}
    
    async def _fetch_brand_context(self) -> Optional[str]:
        """Fetch brand context/about information"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._extract_brand_context(html)
                else:
                    logger.warning(f"Failed to fetch homepage for brand context: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching brand context: {str(e)}")
            return None
    
    async def _fetch_important_links(self) -> Dict[str, str]:
        """Fetch important links like order tracking, contact, blogs"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._extract_important_links(html)
                else:
                    logger.warning(f"Failed to fetch homepage for important links: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching important links: {str(e)}")
            return {}
    
    async def _fetch_metadata(self) -> Dict[str, Any]:
        """Fetch store metadata"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._extract_metadata(html)
                else:
                    logger.warning(f"Failed to fetch homepage for metadata: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching metadata: {str(e)}")
            return {}
    
    def _extract_brand_context(self, html: str) -> Optional[str]:
        """Extract brand context from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for common about/brand sections
            selectors = [
                '[class*="about"]',
                '[class*="brand"]',
                '[class*="story"]',
                '[class*="mission"]',
                '[id*="about"]',
                '[id*="brand"]',
                '[id*="story"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 50:  # Minimum meaningful length
                        return text
            
            # Fallback: look for meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                return meta_desc['content']
            
            return None
        except Exception as e:
            logger.error(f"Error extracting brand context: {str(e)}")
            return None
    
    def _extract_important_links(self, html: str) -> Dict[str, str]:
        """Extract important links from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = {}
            
            # Common important link patterns
            link_patterns = {
                'order_tracking': ['track', 'order', 'tracking'],
                'contact_us': ['contact', 'contact-us'],
                'blog': ['blog', 'news', 'articles'],
                'about': ['about', 'about-us'],
                'shipping': ['shipping', 'delivery'],
                'size_guide': ['size', 'size-guide', 'sizing']
            }
            
            for link_type, patterns in link_patterns.items():
                for pattern in patterns:
                    elements = soup.find_all('a', href=re.compile(pattern, re.I))
                    for element in elements:
                        href = element.get('href')
                        if href:
                            full_url = urljoin(self.base_url, href)
                            links[link_type] = full_url
                            break
                    if link_type in links:
                        break
            
            return links
        except Exception as e:
            logger.error(f"Error extracting important links: {str(e)}")
            return {}
    
    def _extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            metadata = {}
            
            # Extract title
            title = soup.find('title')
            if title:
                metadata['title'] = title.get_text(strip=True)
            
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    metadata[name] = content
            
            # Extract structured data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        metadata['structured_data'] = data
                    elif isinstance(data, list):
                        metadata['structured_data'] = data[0] if data else {}
                except:
                    continue
            
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}
    
    def _to_dict(self, insights: BrandInsights) -> Dict[str, Any]:
        """Convert BrandInsights object to dictionary"""
        return {
            'store_url': insights.store_url,
            'products': insights.products,
            'hero_products': insights.hero_products,
            'privacy_policy': insights.privacy_policy,
            'return_refund_policy': insights.return_refund_policy,
            'faqs': insights.faqs,
            'social_handles': insights.social_handles,
            'contact_details': insights.contact_details,
            'brand_context': insights.brand_context,
            'important_links': insights.important_links,
            'metadata': insights.metadata
        }
