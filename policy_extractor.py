#!/usr/bin/env python3
"""
Policy Extractor for Shopify Store Insights Fetcher

Developer: Kritika Kumari Mishra
Description: Extracts privacy and return/refund policies from Shopify stores.
"""

import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class PolicyExtractor:
    """Class to extract privacy and return/refund policies from Shopify stores"""
    
    async def extract_policies(self, session, base_url: str) -> Dict[str, str]:
        """
        Extract privacy and return/refund policies
        
        Args:
            session: aiohttp session
            base_url: Base URL of the store
            
        Returns:
            Dictionary containing privacy and return/refund policies
        """
        try:
            policies = {}
            
            # Common policy page URLs
            policy_urls = {
                'privacy': [
                    '/pages/privacy-policy',
                    '/pages/privacy',
                    '/privacy-policy',
                    '/privacy',
                    '/legal/privacy-policy',
                    '/policies/privacy-policy'
                ],
                'return_refund': [
                    '/pages/return-policy',
                    '/pages/refund-policy',
                    '/pages/return-refund-policy',
                    '/return-policy',
                    '/refund-policy',
                    '/return-refund-policy',
                    '/legal/return-policy',
                    '/legal/refund-policy',
                    '/policies/refund-policy',
                    '/policies/return-policy'
                ]
            }
            
            # Try to fetch policies from common URLs
            for policy_type, urls in policy_urls.items():
                for url in urls:
                    full_url = urljoin(base_url, url)
                    try:
                        async with session.get(full_url) as response:
                            if response.status == 200:
                                html = await response.text()
                                content = self._extract_policy_content(html)
                                if content:
                                    policies[policy_type] = content
                                    break
                    except Exception as e:
                        logger.debug(f"Failed to fetch {policy_type} from {full_url}: {str(e)}")
                        continue
            
            # If policies not found, try to find them in footer or legal links
            if not policies:
                await self._find_policies_from_footer(session, base_url, policies)
            
            return policies
            
        except Exception as e:
            logger.error(f"Error extracting policies: {str(e)}")
            return {}
    
    async def _find_policies_from_footer(self, session, base_url: str, policies: Dict[str, str]):
        """Find policy links from footer and fetch their content"""
        try:
            async with session.get(base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for policy links in footer
                    footer = soup.find('footer') or soup.find(class_=re.compile(r'footer', re.I))
                    if footer:
                        policy_links = self._extract_policy_links_from_footer(footer)
                        
                        for policy_type, links in policy_links.items():
                            if policy_type not in policies:
                                for link in links:
                                    try:
                                        full_url = urljoin(base_url, link)
                                        async with session.get(full_url) as response:
                                            if response.status == 200:
                                                html = await response.text()
                                                content = self._extract_policy_content(html)
                                                if content:
                                                    policies[policy_type] = content
                                                    break
                                    except Exception as e:
                                        logger.debug(f"Failed to fetch policy from {link}: {str(e)}")
                                        continue
                    
                    # Also look for policy links in navigation
                    nav = soup.find('nav') or soup.find(class_=re.compile(r'nav', re.I))
                    if nav:
                        policy_links = self._extract_policy_links_from_nav(nav)
                        
                        for policy_type, links in policy_links.items():
                            if policy_type not in policies:
                                for link in links:
                                    try:
                                        full_url = urljoin(base_url, link)
                                        async with session.get(full_url) as response:
                                            if response.status == 200:
                                                html = await response.text()
                                                content = self._extract_policy_content(html)
                                                if content:
                                                    policies[policy_type] = content
                                                    break
                                    except Exception as e:
                                        logger.debug(f"Failed to fetch policy from {link}: {str(e)}")
                                        continue
                        
        except Exception as e:
            logger.error(f"Error finding policies from footer: {str(e)}")
    
    def _extract_policy_links_from_footer(self, footer) -> Dict[str, list]:
        """Extract policy links from footer"""
        policy_links = {'privacy': [], 'return_refund': []}
        
        try:
            # Look for privacy policy links
            privacy_patterns = [
                r'privacy[-\s]?policy',
                r'privacy',
                r'data[-\s]?protection'
            ]
            
            for pattern in privacy_patterns:
                links = footer.find_all('a', href=re.compile(pattern, re.I))
                for link in links:
                    href = link.get('href')
                    if href and href not in policy_links['privacy']:
                        policy_links['privacy'].append(href)
            
            # Look for return/refund policy links
            return_patterns = [
                r'return[-\s]?policy',
                r'refund[-\s]?policy',
                r'return[-\s]?refund',
                r'return',
                r'refund'
            ]
            
            for pattern in return_patterns:
                links = footer.find_all('a', href=re.compile(pattern, re.I))
                for link in links:
                    href = link.get('href')
                    if href and href not in policy_links['return_refund']:
                        policy_links['return_refund'].append(href)
            
            return policy_links
            
        except Exception as e:
            logger.error(f"Error extracting policy links from footer: {str(e)}")
            return policy_links
    
    def _extract_policy_links_from_nav(self, nav) -> Dict[str, list]:
        """Extract policy links from navigation"""
        policy_links = {'privacy': [], 'return_refund': []}
        
        try:
            # Look for legal/policies section in navigation
            legal_links = nav.find_all('a', text=re.compile(r'legal|policies|terms', re.I))
            
            for link in legal_links:
                href = link.get('href')
                if href:
                    # Check if it's a privacy or return policy link
                    if re.search(r'privacy', href, re.I):
                        policy_links['privacy'].append(href)
                    elif re.search(r'return|refund', href, re.I):
                        policy_links['return_refund'].append(href)
            
            return policy_links
            
        except Exception as e:
            logger.error(f"Error extracting policy links from nav: {str(e)}")
            return policy_links
    
    def _extract_policy_content(self, html: str) -> Optional[str]:
        """Extract policy content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Look for main content area
            content_selectors = [
                'main',
                '[role="main"]',
                '.main-content',
                '.content',
                '.page-content',
                '.policy-content',
                '.legal-content',
                'article'
            ]
            
            content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator=' ', strip=True)
                    if len(content) > 100:  # Minimum meaningful length
                        break
            
            # If no main content found, try to get all text
            if not content or len(content) < 100:
                content = soup.get_text(separator=' ', strip=True)
            
            # Clean up the content
            if content:
                # Remove extra whitespace
                content = re.sub(r'\s+', ' ', content)
                # Remove common navigation text
                content = re.sub(r'(Home|Shop|About|Contact|Cart|Account|Login|Register|Search|Menu|Close|Back|Next|Previous)', '', content, flags=re.I)
                # Clean up again
                content = re.sub(r'\s+', ' ', content).strip()
                
                # Only return if content is meaningful
                if len(content) > 200:
                    return content
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting policy content: {str(e)}")
            return None
