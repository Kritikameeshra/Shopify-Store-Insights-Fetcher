#!/usr/bin/env python3
"""
FAQ Extractor for Shopify Store Insights Fetcher

Developer: Kritika Kumari Mishra
Description: Extracts FAQ data from Shopify stores using multiple strategies.
"""

import re
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class FAQExtractor:
    """Class to extract FAQs from Shopify stores"""
    
    async def extract_faqs(self, session, base_url: str) -> List[Dict[str, str]]:
        """
        Extract FAQs from the store
        
        Args:
            session: aiohttp session
            base_url: Base URL of the store
            
        Returns:
            List of FAQ dictionaries with question and answer
        """
        try:
            faqs = []
            
            # Common FAQ page URLs
            faq_urls = [
                '/pages/faq',
                '/pages/frequently-asked-questions',
                '/pages/help',
                '/pages/support',
                '/faq',
                '/frequently-asked-questions',
                '/help',
                '/support',
                '/pages/faqs',
                '/faqs'
            ]
            
            # Try to fetch FAQs from common URLs
            for url in faq_urls:
                full_url = urljoin(base_url, url)
                try:
                    async with session.get(full_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            page_faqs = self._extract_faqs_from_page(html)
                            if page_faqs:
                                faqs.extend(page_faqs)
                                break
                except Exception as e:
                    logger.debug(f"Failed to fetch FAQs from {full_url}: {str(e)}")
                    continue
            
            # If no FAQs found, try to find FAQ links in footer or navigation
            if not faqs:
                await self._find_faqs_from_footer(session, base_url, faqs)
            
            # Also try to extract FAQs from homepage
            if not faqs:
                await self._extract_faqs_from_homepage(session, base_url, faqs)
            
            return faqs[:50]  # Limit to 50 FAQs
            
        except Exception as e:
            logger.error(f"Error extracting FAQs: {str(e)}")
            return []
    
    async def _find_faqs_from_footer(self, session, base_url: str, faqs: List[Dict[str, str]]):
        """Find FAQ links from footer and fetch their content"""
        try:
            async with session.get(base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for FAQ links in footer
                    footer = soup.find('footer') or soup.find(class_=re.compile(r'footer', re.I))
                    if footer:
                        faq_links = self._extract_faq_links_from_footer(footer)
                        
                        for link in faq_links:
                            try:
                                full_url = urljoin(base_url, link)
                                async with session.get(full_url) as response:
                                    if response.status == 200:
                                        html = await response.text()
                                        page_faqs = self._extract_faqs_from_page(html)
                                        if page_faqs:
                                            faqs.extend(page_faqs)
                            except Exception as e:
                                logger.debug(f"Failed to fetch FAQ from {link}: {str(e)}")
                                continue
                        
        except Exception as e:
            logger.error(f"Error finding FAQs from footer: {str(e)}")
    
    async def _extract_faqs_from_homepage(self, session, base_url: str, faqs: List[Dict[str, str]]):
        """Extract FAQs from homepage"""
        try:
            async with session.get(base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    page_faqs = self._extract_faqs_from_page(html)
                    if page_faqs:
                        faqs.extend(page_faqs)
                        
        except Exception as e:
            logger.error(f"Error extracting FAQs from homepage: {str(e)}")
    
    def _extract_faq_links_from_footer(self, footer) -> List[str]:
        """Extract FAQ links from footer"""
        faq_links = []
        
        try:
            # Look for FAQ links
            faq_patterns = [
                r'faq',
                r'frequently[-\s]?asked[-\s]?questions',
                r'help',
                r'support'
            ]
            
            for pattern in faq_patterns:
                links = footer.find_all('a', href=re.compile(pattern, re.I))
                for link in links:
                    href = link.get('href')
                    if href and href not in faq_links:
                        faq_links.append(href)
            
            return faq_links
            
        except Exception as e:
            logger.error(f"Error extracting FAQ links from footer: {str(e)}")
            return faq_links
    
    def _extract_faqs_from_page(self, html: str) -> List[Dict[str, str]]:
        """Extract FAQs from a single page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            faqs = []
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try different FAQ extraction methods
            methods = [
                self._extract_faqs_by_accordion,
                self._extract_faqs_by_qa_pattern,
                self._extract_faqs_by_heading_pattern,
                self._extract_faqs_by_list_pattern
            ]
            
            for method in methods:
                try:
                    method_faqs = method(soup)
                    if method_faqs:
                        faqs.extend(method_faqs)
                        break  # Use the first successful method
                except Exception as e:
                    logger.debug(f"FAQ extraction method failed: {str(e)}")
                    continue
            
            return faqs
            
        except Exception as e:
            logger.error(f"Error extracting FAQs from page: {str(e)}")
            return []
    
    def _extract_faqs_by_accordion(self, soup) -> List[Dict[str, str]]:
        """Extract FAQs from accordion-style elements"""
        faqs = []
        
        # Common accordion selectors
        accordion_selectors = [
            '[class*="accordion"]',
            '[class*="faq"]',
            '[class*="collapse"]',
            '[data-toggle="collapse"]',
            '[aria-expanded]'
        ]
        
        for selector in accordion_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Look for question and answer within the element
                question = self._extract_question_from_element(element)
                answer = self._extract_answer_from_element(element)
                
                if question and answer:
                    faqs.append({
                        'question': question,
                        'answer': answer
                    })
        
        return faqs
    
    def _extract_faqs_by_qa_pattern(self, soup) -> List[Dict[str, str]]:
        """Extract FAQs by looking for Q&A patterns in text"""
        faqs = []
        
        # Look for Q&A patterns
        qa_patterns = [
            r'Q[:\s]*([^A]+)A[:\s]*(.+)',
            r'Question[:\s]*([^A]+)Answer[:\s]*(.+)',
            r'([^?]+\?)\s*([^?]+)'
        ]
        
        text = soup.get_text()
        
        for pattern in qa_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    question = match.group(1).strip()
                    answer = match.group(2).strip()
                    
                    # Clean up the text
                    question = re.sub(r'\s+', ' ', question)
                    answer = re.sub(r'\s+', ' ', answer)
                    
                    if len(question) > 10 and len(answer) > 20:
                        faqs.append({
                            'question': question,
                            'answer': answer
                        })
        
        return faqs
    
    def _extract_faqs_by_heading_pattern(self, soup) -> List[Dict[str, str]]:
        """Extract FAQs by looking for heading patterns"""
        faqs = []
        
        # Look for headings that might be questions
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for i, heading in enumerate(headings):
            heading_text = heading.get_text(strip=True)
            
            # Check if heading looks like a question
            if self._is_question(heading_text):
                # Look for answer in next elements
                answer = self._find_answer_after_heading(heading)
                
                if answer:
                    faqs.append({
                        'question': heading_text,
                        'answer': answer
                    })
        
        return faqs
    
    def _extract_faqs_by_list_pattern(self, soup) -> List[Dict[str, str]]:
        """Extract FAQs from list patterns"""
        faqs = []
        
        # Look for lists that might contain FAQs
        lists = soup.find_all(['ul', 'ol', 'dl'])
        
        for list_elem in lists:
            items = list_elem.find_all(['li', 'dt', 'dd'])
            
            for i in range(0, len(items) - 1, 2):
                if i + 1 < len(items):
                    question_elem = items[i]
                    answer_elem = items[i + 1]
                    
                    question = question_elem.get_text(strip=True)
                    answer = answer_elem.get_text(strip=True)
                    
                    if self._is_question(question) and len(answer) > 10:
                        faqs.append({
                            'question': question,
                            'answer': answer
                        })
        
        return faqs
    
    def _extract_question_from_element(self, element) -> str:
        """Extract question from an element"""
        # Look for question in common selectors
        question_selectors = [
            '[class*="question"]',
            '[class*="title"]',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'b'
        ]
        
        for selector in question_selectors:
            question_elem = element.select_one(selector)
            if question_elem:
                question = question_elem.get_text(strip=True)
                if self._is_question(question):
                    return question
        
        # Fallback: get first text that looks like a question
        text = element.get_text(strip=True)
        lines = text.split('\n')
        for line in lines:
            if self._is_question(line.strip()):
                return line.strip()
        
        return ""
    
    def _extract_answer_from_element(self, element) -> str:
        """Extract answer from an element"""
        # Look for answer in common selectors
        answer_selectors = [
            '[class*="answer"]',
            '[class*="content"]',
            '[class*="body"]',
            'p',
            'div'
        ]
        
        for selector in answer_selectors:
            answer_elem = element.select_one(selector)
            if answer_elem:
                answer = answer_elem.get_text(strip=True)
                if len(answer) > 10:
                    return answer
        
        # Fallback: get all text and remove question
        text = element.get_text(strip=True)
        lines = text.split('\n')
        
        # Find the first line that's not a question
        for line in lines:
            line = line.strip()
            if line and not self._is_question(line) and len(line) > 10:
                return line
        
        return ""
    
    def _is_question(self, text: str) -> bool:
        """Check if text looks like a question"""
        if not text:
            return False
        
        # Check for question marks
        if '?' in text:
            return True
        
        # Check for question words
        question_words = [
            'what', 'when', 'where', 'who', 'why', 'how',
            'can', 'could', 'would', 'should', 'will', 'do',
            'does', 'did', 'is', 'are', 'was', 'were'
        ]
        
        text_lower = text.lower()
        for word in question_words:
            if text_lower.startswith(word + ' '):
                return True
        
        return False
    
    def _find_answer_after_heading(self, heading) -> str:
        """Find answer text after a heading"""
        answer = ""
        current = heading.next_sibling
        
        # Look for next few elements
        for _ in range(5):
            if current is None:
                break
            
            if hasattr(current, 'get_text'):
                text = current.get_text(strip=True)
                if text and len(text) > 10:
                    answer = text
                    break
            
            current = current.next_sibling
        
        return answer
