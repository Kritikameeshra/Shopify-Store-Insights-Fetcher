#!/usr/bin/env python3
"""
Contact Extractor for Shopify Store Insights Fetcher

Developer: Kritika Kumari Mishra
Description: Extracts contact information including emails, phone numbers, and addresses.
"""

import re
from typing import Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class ContactExtractor:
    """Class to extract contact details from Shopify stores"""
    
    async def extract_contact_details(self, session, base_url: str) -> Dict[str, str]:
        """
        Extract contact details from the store
        
        Args:
            session: aiohttp session
            base_url: Base URL of the store
            
        Returns:
            Dictionary containing contact details
        """
        try:
            contact_details = {}
            
            # Common contact page URLs
            contact_urls = [
                '/pages/contact',
                '/pages/contact-us',
                '/contact',
                '/contact-us',
                '/pages/contact-form',
                '/contact-form'
            ]
            
            # Try to fetch contact details from common URLs
            for url in contact_urls:
                full_url = urljoin(base_url, url)
                try:
                    async with session.get(full_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            page_contacts = self._extract_contact_details_from_page(html)
                            if page_contacts:
                                contact_details.update(page_contacts)
                                break
                except Exception as e:
                    logger.debug(f"Failed to fetch contact details from {full_url}: {str(e)}")
                    continue
            
            # If no contact details found, try to find them in footer or navigation
            if not contact_details:
                await self._find_contact_details_from_footer(session, base_url, contact_details)
            
            # Also try to extract contact details from homepage
            if not contact_details:
                await self._extract_contact_details_from_homepage(session, base_url, contact_details)
            
            return contact_details
            
        except Exception as e:
            logger.error(f"Error extracting contact details: {str(e)}")
            return {}
    
    async def _find_contact_details_from_footer(self, session, base_url: str, contact_details: Dict[str, str]):
        """Find contact details from footer and fetch their content"""
        try:
            async with session.get(base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for contact details in footer
                    footer = soup.find('footer') or soup.find(class_=re.compile(r'footer', re.I))
                    if footer:
                        footer_contacts = self._extract_contact_details_from_footer(footer)
                        contact_details.update(footer_contacts)
                    
                    # Also look for contact details in header/navigation
                    header = soup.find('header') or soup.find(class_=re.compile(r'header|nav', re.I))
                    if header:
                        header_contacts = self._extract_contact_details_from_header(header)
                        contact_details.update(header_contacts)
                        
        except Exception as e:
            logger.error(f"Error finding contact details from footer: {str(e)}")
    
    async def _extract_contact_details_from_homepage(self, session, base_url: str, contact_details: Dict[str, str]):
        """Extract contact details from homepage"""
        try:
            async with session.get(base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    page_contacts = self._extract_contact_details_from_page(html)
                    if page_contacts:
                        contact_details.update(page_contacts)
                        
        except Exception as e:
            logger.error(f"Error extracting contact details from homepage: {str(e)}")
    
    def _extract_contact_details_from_page(self, html: str) -> Dict[str, str]:
        """Extract contact details from a single page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            contact_details = {}
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract email addresses
            emails = self._extract_emails(soup)
            if emails:
                contact_details['emails'] = ', '.join(emails)
            
            # Extract phone numbers
            phones = self._extract_phone_numbers(soup)
            if phones:
                contact_details['phone_numbers'] = ', '.join(phones)
            
            # Extract addresses
            address = self._extract_address(soup)
            if address:
                contact_details['address'] = address
            
            # Extract social media links
            social_links = self._extract_social_links(soup)
            if social_links:
                contact_details['social_links'] = social_links
            
            # Extract contact form
            contact_form = self._extract_contact_form(soup)
            if contact_form:
                contact_details['contact_form'] = contact_form
            
            return contact_details
            
        except Exception as e:
            logger.error(f"Error extracting contact details from page: {str(e)}")
            return {}
    
    def _extract_contact_details_from_footer(self, footer) -> Dict[str, str]:
        """Extract contact details from footer"""
        contact_details = {}
        
        try:
            # Extract emails
            emails = self._extract_emails(footer)
            if emails:
                contact_details['emails'] = ', '.join(emails)
            
            # Extract phone numbers
            phones = self._extract_phone_numbers(footer)
            if phones:
                contact_details['phone_numbers'] = ', '.join(phones)
            
            # Extract address
            address = self._extract_address(footer)
            if address:
                contact_details['address'] = address
            
            return contact_details
            
        except Exception as e:
            logger.error(f"Error extracting contact details from footer: {str(e)}")
            return contact_details
    
    def _extract_contact_details_from_header(self, header) -> Dict[str, str]:
        """Extract contact details from header"""
        contact_details = {}
        
        try:
            # Extract emails
            emails = self._extract_emails(header)
            if emails:
                contact_details['emails'] = ', '.join(emails)
            
            # Extract phone numbers
            phones = self._extract_phone_numbers(header)
            if phones:
                contact_details['phone_numbers'] = ', '.join(phones)
            
            return contact_details
            
        except Exception as e:
            logger.error(f"Error extracting contact details from header: {str(e)}")
            return contact_details
    
    def _extract_emails(self, element) -> list:
        """Extract email addresses from element"""
        emails = []
        
        try:
            # Look for mailto links
            mailto_links = element.find_all('a', href=re.compile(r'^mailto:', re.I))
            for link in mailto_links:
                href = link.get('href')
                if href:
                    email = href.replace('mailto:', '').split('?')[0]
                    if self._is_valid_email(email):
                        emails.append(email)
            
            # Look for email patterns in text
            text = element.get_text()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.findall(email_pattern, text)
            
            for email in email_matches:
                if self._is_valid_email(email) and email not in emails:
                    emails.append(email)
            
            return emails
            
        except Exception as e:
            logger.error(f"Error extracting emails: {str(e)}")
            return emails
    
    def _extract_phone_numbers(self, element) -> list:
        """Extract phone numbers from element"""
        phones = []
        
        try:
            # Look for tel links
            tel_links = element.find_all('a', href=re.compile(r'^tel:', re.I))
            for link in tel_links:
                href = link.get('href')
                if href:
                    phone = href.replace('tel:', '').replace('+', '').replace('-', '').replace(' ', '')
                    if self._is_valid_phone(phone):
                        phones.append(phone)
            
            # Look for phone patterns in text
            text = element.get_text()
            
            # Various phone number patterns
            phone_patterns = [
                r'\+?[\d\s\-\(\)]{10,}',  # International format
                r'[\d\s\-\(\)]{10,}',     # Local format
                r'\+?[\d\s\-]{10,}',      # Simple format
            ]
            
            for pattern in phone_patterns:
                phone_matches = re.findall(pattern, text)
                for phone in phone_matches:
                    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
                    if self._is_valid_phone(clean_phone) and clean_phone not in phones:
                        phones.append(clean_phone)
            
            return phones
            
        except Exception as e:
            logger.error(f"Error extracting phone numbers: {str(e)}")
            return phones
    
    def _extract_address(self, element) -> str:
        """Extract address from element"""
        try:
            # Look for address elements
            address_elem = element.find('address')
            if address_elem:
                address = address_elem.get_text(strip=True)
                if len(address) > 10:
                    return address
            
            # Look for address in common selectors
            address_selectors = [
                '[class*="address"]',
                '[class*="location"]',
                '[class*="contact"]'
            ]
            
            for selector in address_selectors:
                addr_elem = element.select_one(selector)
                if addr_elem:
                    address = addr_elem.get_text(strip=True)
                    if len(address) > 10:
                        return address
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting address: {str(e)}")
            return ""
    
    def _extract_social_links(self, element) -> str:
        """Extract social media links from element"""
        try:
            social_links = []
            
            # Common social media platforms
            social_platforms = [
                'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
                'youtube.com', 'tiktok.com', 'pinterest.com', 'snapchat.com'
            ]
            
            links = element.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').lower()
                for platform in social_platforms:
                    if platform in href:
                        social_links.append(href)
                        break
            
            return ', '.join(social_links) if social_links else ""
            
        except Exception as e:
            logger.error(f"Error extracting social links: {str(e)}")
            return ""
    
    def _extract_contact_form(self, element) -> str:
        """Extract contact form information"""
        try:
            # Look for contact form
            form = element.find('form')
            if form:
                # Check if it's a contact form
                form_text = form.get_text().lower()
                if any(word in form_text for word in ['contact', 'message', 'inquiry', 'support']):
                    return "Contact form available"
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting contact form: {str(e)}")
            return ""
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid"""
        if not email:
            return False
        
        # Basic email validation
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Check if phone number is valid"""
        if not phone:
            return False
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it has reasonable length (7-15 digits)
        return 7 <= len(digits_only) <= 15
