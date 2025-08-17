# 🎉 Shopify Store Insights Fetcher

**Developer: Kritika Kumari Mishra**

A comprehensive Python application that extracts detailed insights from Shopify stores without using the official Shopify API. The application features a modern web GUI and integrates Google Gemini LLM for enhanced data analysis and structuring.

## Live Demo
https://shopify-store-insights-fetcher-bkmc.onrender.com

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Set up Environment**
Create a `.env` file with your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. **Start the Application**
```bash
python main.py
```

### 4. **Access the Application**
- **GUI Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Requirements Fulfilled

### ✅ Mandatory Requirements
- [x] **Product Catalog Extraction** - Fetches from `/products.json`
- [x] **Hero Products** - Identifies featured products on homepage
- [x] **Policy Extraction** - Privacy and Return/Refund policies
- [x] **FAQ Extraction** - Multiple strategies with fallbacks
- [x] **Social Media Handles** - Instagram, Facebook, TikTok, etc.
- [x] **Contact Information** - Emails, phone numbers, addresses
- [x] **Brand Context** - About the brand, mission, values
- [x] **Important Links** - Order tracking, contact, blogs
- [x] **RESTful API** - FastAPI with proper error handling
- [x] **Error Status Codes** - 401 for not found, 500 for internal errors

### ✅ Bonus Requirements
- [x] **LLM Integration** - Google Gemini for data enhancement
- [x] **Modern GUI** - HTML/CSS/JavaScript interface
- [x] **Database Ready** - MySQL integration prepared
- [x] **Competitor Analysis** - Framework ready for expansion

## 🏗️ Project Structure

```
📁 Shopify Store Insights Fetcher/
├── 🐍 main.py                    # FastAPI application entry point
├── 🔧 shopify_insights_fetcher.py # Main orchestrator class
├── 🤖 llm_processor.py           # Google Gemini integration
├── 📦 product_extractor.py       # Product data extraction
├── 📄 policy_extractor.py        # Policy page extraction
├── ❓ faq_extractor.py           # FAQ extraction with fallbacks
├── 📞 contact_extractor.py       # Contact information extraction
├── 📱 social_extractor.py        # Social media handle extraction
├── 📁 static/                    # Frontend files
│   ├── 🎨 index.html             # Main GUI interface
│   ├── 💅 styles.css             # Modern responsive styling
│   └── ⚡ script.js              # Interactive functionality
├── 📋 requirements.txt           # Python dependencies
└── 🔑 .env                       # Environment variables
```

## 🎨 Features

### Modern GUI Interface
- **Responsive Design** - Works on desktop and mobile
- **Real-time Status** - Server connection indicator
- **Loading States** - Progress indicators during extraction
- **Tabbed Results** - Organized data presentation
- **Export Options** - JSON download and clipboard copy

### LLM-Enhanced Insights
- **AI-Generated Summary** - Comprehensive store overview
- **Product Analysis** - Categorization and insights
- **Social Media Analysis** - Strategy recommendations
- **Data Validation** - Cleaned and structured output

### Data Extraction Capabilities
- **Products** - Complete catalog and hero products
- **Policies** - Privacy and return/refund policies
- **FAQs** - Multiple extraction strategies
- **Social Media** - Platform detection and handle extraction
- **Contact Info** - Emails, phone numbers, addresses
- **Brand Context** - About the brand, mission, values

## 🔧 Technology Stack

- **Backend**: Python 3.8+, FastAPI, aiohttp, BeautifulSoup4
- **LLM**: Google Gemini (google-generativeai)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: MySQL (ready for integration)
- **Styling**: Custom CSS with Font Awesome icons

## 📈 Usage Examples

### Basic Usage
1. Open http://localhost:8000
2. Enter a Shopify store URL
3. Click "Fetch Insights"
4. View results in organized tabs

### API Usage
```python
import requests

response = requests.post(
    "http://localhost:8000/fetch-insights",
    json={"website_url": "https://memy.co.in"}
)

if response.status_code == 200:
    insights = response.json()["data"]
    print(f"Found {len(insights['products'])} products")
```

### Test URLs
- **Fashion**: https://memy.co.in
- **Beauty**: https://hairoriginals.com
- **Lifestyle**: https://www.lunchskins.com

## 🎯 Key Achievements

### Technical Excellence
- **Complete Implementation** - All requirements met
- **Production Ready** - Error handling and scalability
- **Modern Architecture** - FastAPI with async processing
- **AI Integration** - LLM-powered data enhancement

### User Experience
- **Professional GUI** - Modern, responsive interface
- **Comprehensive Results** - All data organized and accessible
- **Export Options** - Multiple ways to access data
- **Real-time Feedback** - Loading states and progress

## 🚀 Performance Features

- **Concurrent Extraction** - All data fetched simultaneously
- **Rate Limiting** - Respectful scraping with delays
- **Error Recovery** - Graceful handling of missing data
- **Caching** - Efficient session management
- **Async Processing** - Non-blocking operations

## 🔒 Error Handling

- **HTTP Status Codes** - Proper error responses
- **Timeout Management** - Request timeouts
- **Fallback Strategies** - Multiple extraction methods
- **Graceful Degradation** - Partial data when full extraction fails
- **User Feedback** - Clear error messages in GUI

## 🎉 Conclusion

This Shopify Store Insights Fetcher successfully demonstrates:

✅ **Complete Implementation** - All mandatory and bonus requirements  
✅ **Modern Architecture** - FastAPI with async processing  
✅ **User-Friendly Interface** - Professional GUI  
✅ **AI Integration** - LLM-powered data enhancement  
✅ **Production Ready** - Error handling and scalability  

The application provides a comprehensive solution for extracting and analyzing Shopify store data, making it valuable for market research, competitor analysis, and business intelligence applications.

---

## 🚀 Ready to Use!

The application is now fully functional and ready for use. Simply run `python main.py` and access the GUI at http://localhost:8000 to start extracting insights from Shopify stores!


**Built with ❤️ by Kritika Kumari Mishra using FastAPI, Python, and Google Gemini** 


