#!/usr/bin/env python3
"""
Social Media Extractor for Shopify Store Insights Fetcher

Developer: Kritika Kumari Mishra
Description: Extracts social media handles and links from Shopify stores.
"""

import re
from typing import Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class SocialExtractor:
    """Class to extract social media handles from Shopify stores"""
    
    def extract_social_handles(self, html: str) -> Dict[str, str]:
        """
        Extract social media handles from HTML
        
        Args:
            html: HTML content of the page
            
        Returns:
            Dictionary containing social media handles
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            social_handles = {}
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract social media handles
            social_handles.update(self._extract_social_links(soup))
            social_handles.update(self._extract_social_handles_from_text(soup))
            social_handles.update(self._extract_social_meta_tags(soup))
            
            return social_handles
            
        except Exception as e:
            logger.error(f"Error extracting social handles: {str(e)}")
            return {}
    
    def _extract_social_links(self, soup) -> Dict[str, str]:
        """Extract social media links from anchor tags"""
        social_handles = {}
        
        try:
            # Common social media platforms and their patterns
            social_platforms = {
                'instagram': [
                    r'instagram\.com/([^/\s?]+)',
                    r'@([^/\s]+)',
                    r'instagram\.com/([^/\s?]+)'
                ],
                'facebook': [
                    r'facebook\.com/([^/\s?]+)',
                    r'fb\.com/([^/\s?]+)'
                ],
                'twitter': [
                    r'twitter\.com/([^/\s?]+)',
                    r'x\.com/([^/\s?]+)'
                ],
                'youtube': [
                    r'youtube\.com/([^/\s?]+)',
                    r'youtube\.com/channel/([^/\s?]+)',
                    r'youtube\.com/user/([^/\s?]+)'
                ],
                'tiktok': [
                    r'tiktok\.com/@([^/\s?]+)',
                    r'tiktok\.com/([^/\s?]+)'
                ],
                'linkedin': [
                    r'linkedin\.com/company/([^/\s?]+)',
                    r'linkedin\.com/in/([^/\s?]+)'
                ],
                'pinterest': [
                    r'pinterest\.com/([^/\s?]+)'
                ],
                'snapchat': [
                    r'snapchat\.com/add/([^/\s?]+)'
                ],
                'whatsapp': [
                    r'wa\.me/([^/\s?]+)',
                    r'whatsapp\.com/([^/\s?]+)'
                ]
            }
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').lower()
                link_text = link.get_text(strip=True).lower()
                
                for platform, patterns in social_platforms.items():
                    for pattern in patterns:
                        match = re.search(pattern, href, re.I)
                        if match:
                            handle = match.group(1)
                            if handle and len(handle) > 1:
                                social_handles[platform] = handle
                                break
                    
                    # Also check link text for @ handles
                    if platform not in social_handles:
                        at_pattern = r'@([^/\s]+)'
                        at_match = re.search(at_pattern, link_text)
                        if at_match:
                            handle = at_match.group(1)
                            if handle and len(handle) > 1:
                                social_handles[platform] = handle
            
            return social_handles
            
        except Exception as e:
            logger.error(f"Error extracting social links: {str(e)}")
            return social_handles
    
    def _extract_social_handles_from_text(self, soup) -> Dict[str, str]:
        """Extract social media handles from text content"""
        social_handles = {}
        
        try:
            text = soup.get_text()
            
            # Common social media handle patterns
            handle_patterns = {
                'instagram': [
                    r'@([a-zA-Z0-9._]+)',
                    r'instagram\.com/([a-zA-Z0-9._]+)',
                    r'instagram:?\s*@?([a-zA-Z0-9._]+)'
                ],
                'facebook': [
                    r'facebook\.com/([a-zA-Z0-9._]+)',
                    r'fb\.com/([a-zA-Z0-9._]+)',
                    r'facebook:?\s*([a-zA-Z0-9._]+)'
                ],
                'twitter': [
                    r'twitter\.com/([a-zA-Z0-9._]+)',
                    r'x\.com/([a-zA-Z0-9._]+)',
                    r'twitter:?\s*@?([a-zA-Z0-9._]+)'
                ],
                'youtube': [
                    r'youtube\.com/([a-zA-Z0-9._]+)',
                    r'youtube\.com/channel/([a-zA-Z0-9._]+)',
                    r'youtube:?\s*([a-zA-Z0-9._]+)'
                ],
                'tiktok': [
                    r'tiktok\.com/@([a-zA-Z0-9._]+)',
                    r'tiktok:?\s*@?([a-zA-Z0-9._]+)'
                ],
                'linkedin': [
                    r'linkedin\.com/company/([a-zA-Z0-9._]+)',
                    r'linkedin\.com/in/([a-zA-Z0-9._]+)',
                    r'linkedin:?\s*([a-zA-Z0-9._]+)'
                ],
                'pinterest': [
                    r'pinterest\.com/([a-zA-Z0-9._]+)',
                    r'pinterest:?\s*([a-zA-Z0-9._]+)'
                ],
                'snapchat': [
                    r'snapchat\.com/add/([a-zA-Z0-9._]+)',
                    r'snapchat:?\s*([a-zA-Z0-9._]+)'
                ]
            }
            
            for platform, patterns in handle_patterns.items():
                if platform not in social_handles:
                    for pattern in patterns:
                        matches = re.findall(pattern, text, re.I)
                        for match in matches:
                            if match and len(match) > 1:
                                social_handles[platform] = match
                                break
                        if platform in social_handles:
                            break
            
            return social_handles
            
        except Exception as e:
            logger.error(f"Error extracting social handles from text: {str(e)}")
            return social_handles
    
    def _extract_social_meta_tags(self, soup) -> Dict[str, str]:
        """Extract social media handles from meta tags"""
        social_handles = {}
        
        try:
            # Common social media meta tag patterns
            meta_patterns = {
                'facebook': [
                    'property="og:site_name"',
                    'property="fb:app_id"',
                    'name="facebook-domain-verification"'
                ],
                'twitter': [
                    'name="twitter:site"',
                    'name="twitter:creator"'
                ],
                'instagram': [
                    'property="og:site_name"'
                ],
                'linkedin': [
                    'property="og:site_name"'
                ]
            }
            
            meta_tags = soup.find_all('meta')
            
            for meta in meta_tags:
                content = meta.get('content', '')
                property_attr = meta.get('property', '')
                name_attr = meta.get('name', '')
                
                # Check for social media patterns in content
                for platform, patterns in meta_patterns.items():
                    if platform not in social_handles:
                        for pattern in patterns:
                            if pattern in str(meta):
                                # Try to extract handle from content
                                if content:
                                    # Look for common handle patterns in content
                                    handle_match = re.search(r'([a-zA-Z0-9._]+)', content)
                                    if handle_match:
                                        handle = handle_match.group(1)
                                        if len(handle) > 1:
                                            social_handles[platform] = handle
                                            break
                        if platform in social_handles:
                            break
            
            return social_handles
            
        except Exception as e:
            logger.error(f"Error extracting social meta tags: {str(e)}")
            return social_handles
    
    def _clean_handle(self, handle: str) -> str:
        """Clean and validate a social media handle"""
        if not handle:
            return ""
        
        # Remove common prefixes and suffixes
        handle = re.sub(r'^@+', '', handle)
        handle = re.sub(r'^https?://', '', handle)
        handle = re.sub(r'^www\.', '', handle)
        
        # Remove trailing slashes and query parameters
        handle = handle.split('/')[0]
        handle = handle.split('?')[0]
        handle = handle.split('#')[0]
        
        # Remove invalid characters
        handle = re.sub(r'[^a-zA-Z0-9._-]', '', handle)
        
        return handle.strip()
