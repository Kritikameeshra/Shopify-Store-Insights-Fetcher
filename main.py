#!/usr/bin/env python3
"""
Shopify Store Insights Fetcher - FastAPI Application

Developer: Kritika Kumari Mishra
Description: A comprehensive Python application that extracts detailed insights 
from Shopify stores without using the official Shopify API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import logging
import os

from shopify_insights_fetcher import ShopifyInsightsFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="API to fetch insights from Shopify stores",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


class WebsiteRequest(BaseModel):
    website_url: HttpUrl


class BrandInsightsResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


@app.get("/")
async def root():
    """Serve the main GUI page"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Shopify Store Insights Fetcher API", "version": "1.0.0"}


@app.post("/fetch-insights", response_model=BrandInsightsResponse)
async def fetch_shopify_insights(request: WebsiteRequest):
    """
    Fetch insights from a Shopify store website
    """
    try:
        logger.info(f"Fetching insights for: {request.website_url}")

        # Initialize the fetcher
        fetcher = ShopifyInsightsFetcher()

        # Fetch insights
        insights = await fetcher.fetch_store_insights(str(request.website_url))

        return BrandInsightsResponse(
            success=True,
            data=insights,
            message="Insights fetched successfully"
        )

    except Exception as e:
        logger.error(f"Error fetching insights: {str(e)}")

        if "404" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Website not found")
        elif "401" in str(e) or "unauthorized" in str(e).lower():
            raise HTTPException(status_code=401, detail="Unauthorized access")
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "Shopify Insights Fetcher"}
