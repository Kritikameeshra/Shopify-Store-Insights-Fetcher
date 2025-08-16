#!/usr/bin/env python3
"""
LLM Processor using Google Gemini for enhanced data extraction and structuring

Developer: Kritika Kumari Mishra
Description: Integrates Google Gemini LLM for enhanced data analysis and structuring.
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiProcessor:
    """Process extracted data using Google Gemini LLM for better structuring and insights"""
    
    def __init__(self):
        """Initialize Gemini processor"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables. LLM features will be disabled.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            logger.info("Gemini LLM processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.enabled = False
    
    async def structure_faqs(self, raw_faqs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Use Gemini to structure and improve FAQ extraction"""
        if not self.enabled or not raw_faqs:
            return raw_faqs
        
        try:
            prompt = f"""
            Analyze and structure the following FAQ data from a Shopify store. 
            Clean up the questions and answers, ensure they are properly formatted.
            
            Raw FAQ data:
            {json.dumps(raw_faqs, indent=2)}
            
            Return a JSON array of FAQ objects with 'question' and 'answer' fields.
            Make sure questions are clear and answers are concise but complete.
            """
            
            response = self.model.generate_content(prompt)
            try:
                # Try to parse the response as JSON
                structured_faqs = json.loads(response.text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    try:
                        structured_faqs = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse FAQ JSON, using original data")
                        return raw_faqs
                else:
                    logger.warning("No valid JSON found in FAQ response, using original data")
                    return raw_faqs
            logger.info(f"Structured {len(structured_faqs)} FAQs using Gemini")
            return structured_faqs
            
        except Exception as e:
            logger.error(f"Error structuring FAQs with Gemini: {e}")
            return raw_faqs
    
    async def extract_brand_context(self, html_content: str, metadata: Dict[str, Any]) -> str:
        """Use Gemini to extract comprehensive brand context"""
        if not self.enabled:
            return metadata.get('description', '')
        
        try:
            prompt = f"""
            Extract comprehensive brand context and information from this Shopify store data.
            
            HTML Content (first 2000 characters):
            {html_content[:2000]}
            
            Metadata:
            {json.dumps(metadata, indent=2)}
            
            Provide a comprehensive brand description including:
            - What the brand sells
            - Brand values and mission
            - Target audience
            - Key selling points
            
            Return a well-structured paragraph (max 300 words).
            """
            
            response = self.model.generate_content(prompt)
            brand_context = response.text.strip()
            logger.info("Extracted brand context using Gemini")
            return brand_context
            
        except Exception as e:
            logger.error(f"Error extracting brand context with Gemini: {e}")
            return metadata.get('description', '')
    
    async def categorize_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use Gemini to categorize and analyze products"""
        if not self.enabled or not products:
            return {"categories": {}, "analysis": ""}
        
        try:
            # Sample products for analysis
            sample_products = products[:10] if len(products) > 10 else products
            
            prompt = f"""
            Analyze these Shopify store products and provide:
            1. Product categories and their counts
            2. Price range analysis
            3. Key product insights
            
            Products:
            {json.dumps(sample_products, indent=2)}
            
            Return a JSON object with:
            - "categories": object with category names and counts
            - "analysis": string with key insights about the product catalog
            """
            
            response = self.model.generate_content(prompt)
            try:
                # Try to parse the response as JSON
                analysis = json.loads(response.text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse product analysis JSON, using default")
                        return {"categories": {}, "analysis": ""}
                else:
                    logger.warning("No valid JSON found in product analysis response, using default")
                    return {"categories": {}, "analysis": ""}
            logger.info("Categorized products using Gemini")
            return analysis
            
        except Exception as e:
            logger.error(f"Error categorizing products with Gemini: {e}")
            return {"categories": {}, "analysis": ""}
    
    async def enhance_social_analysis(self, social_handles: Dict[str, str]) -> Dict[str, Any]:
        """Use Gemini to analyze social media presence"""
        if not self.enabled or not social_handles:
            return {"analysis": "", "recommendations": []}
        
        try:
            prompt = f"""
            Analyze this Shopify store's social media presence and provide insights.
            
            Social Handles:
            {json.dumps(social_handles, indent=2)}
            
            Provide:
            1. Analysis of social media strategy
            2. Recommendations for improvement
            3. Platform-specific insights
            
            Return a JSON object with:
            - "analysis": string with social media analysis
            - "recommendations": array of improvement suggestions
            """
            
            response = self.model.generate_content(prompt)
            try:
                # Try to parse the response as JSON
                analysis = json.loads(response.text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse social analysis JSON, using default")
                        return {"analysis": "", "recommendations": []}
                else:
                    logger.warning("No valid JSON found in social analysis response, using default")
                    return {"analysis": "", "recommendations": []}
            logger.info("Enhanced social media analysis using Gemini")
            return analysis
            
        except Exception as e:
            logger.error(f"Error enhancing social analysis with Gemini: {e}")
            return {"analysis": "", "recommendations": []}
    
    async def generate_insights_summary(self, insights: Dict[str, Any]) -> str:
        """Use Gemini to generate a comprehensive insights summary"""
        if not self.enabled:
            return "Insights extracted successfully"
        
        try:
            # Create a summary of key data points
            summary_data = {
                "total_products": len(insights.get('products', [])),
                "hero_products": len(insights.get('hero_products', [])),
                "faqs_count": len(insights.get('faqs', [])),
                "social_platforms": len(insights.get('social_handles', {})),
                "has_policies": bool(insights.get('privacy_policy') or insights.get('return_refund_policy')),
                "contact_info": bool(insights.get('contact_details')),
                "brand_context": bool(insights.get('brand_context'))
            }
            
            prompt = f"""
            Generate a comprehensive summary of Shopify store insights.
            
            Store URL: {insights.get('store_url', 'N/A')}
            Data Summary: {json.dumps(summary_data, indent=2)}
            
            Provide a professional summary including:
            - Store overview
            - Key metrics
            - Data completeness assessment
            - Notable findings
            
            Keep it concise but informative (max 200 words).
            """
            
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            logger.info("Generated insights summary using Gemini")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating insights summary with Gemini: {e}")
            return "Insights extracted successfully"
    
    async def validate_and_clean_data(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini to validate and clean extracted data"""
        if not self.enabled:
            return insights
        
        try:
            prompt = f"""
            Validate and clean this Shopify store insights data.
            
            Raw Insights:
            {json.dumps(insights, indent=2)}
            
            Tasks:
            1. Remove any duplicate or invalid entries
            2. Validate email formats and phone numbers
            3. Clean up social media handles
            4. Ensure consistent formatting
            
            Return the cleaned JSON data.
            """
            
            response = self.model.generate_content(prompt)
            try:
                # Try to parse the response as JSON
                cleaned_insights = json.loads(response.text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        cleaned_insights = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse validation JSON, using original data")
                        return insights
                else:
                    logger.warning("No valid JSON found in validation response, using original data")
                    return insights
            logger.info("Validated and cleaned data using Gemini")
            return cleaned_insights
            
        except Exception as e:
            logger.error(f"Error validating data with Gemini: {e}")
            return insights
