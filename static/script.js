// Global variables
let currentResults = null;
const API_BASE_URL = 'http://localhost:8000';

// DOM elements
const elements = {
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    insightsForm: document.getElementById('insightsForm'),
    websiteUrlInput: document.getElementById('websiteUrl'),
    fetchBtn: document.getElementById('fetchBtn'),
    clearBtn: document.getElementById('clearBtn'),
    loadingSection: document.getElementById('loadingSection'),
    resultsSection: document.getElementById('resultsSection'),
    errorSection: document.getElementById('errorSection'),
    errorMessage: document.getElementById('errorMessage'),
    summaryCards: document.getElementById('summaryCards'),
    overviewContent: document.getElementById('overviewContent'),
    productsContent: document.getElementById('productsContent'),
    policiesContent: document.getElementById('policiesContent'),
    faqsContent: document.getElementById('faqsContent'),
    contactContent: document.getElementById('contactContent'),
    socialContent: document.getElementById('socialContent'),
    llmContent: document.getElementById('llmContent'),
    rawJson: document.getElementById('rawJson'),
    exportBtn: document.getElementById('exportBtn'),
    copyBtn: document.getElementById('copyBtn'),
    toastContainer: document.getElementById('toastContainer')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkServerStatus();
});

// Initialize the application
function initializeApp() {
    console.log('🚀 Shopify Insights Fetcher GUI initialized');
    updateStatus('Connecting to server...', 'connecting');
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    elements.insightsForm.addEventListener('submit', handleFormSubmit);
    
    // Clear results button
    elements.clearBtn.addEventListener('click', clearResults);
    
    // Quick test URL buttons
    document.querySelectorAll('.test-url-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            elements.websiteUrlInput.value = url;
            handleFormSubmit(new Event('submit'));
        });
    });
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Export and copy buttons
    elements.exportBtn.addEventListener('click', exportResults);
    elements.copyBtn.addEventListener('click', copyResults);
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateStatus('Connected', 'online');
            showToast('Server connected successfully!', 'success');
        } else {
            updateStatus('Server error', 'offline');
            showToast('Server is not responding properly', 'error');
        }
    } catch (error) {
        updateStatus('Offline', 'offline');
        showToast('Cannot connect to server. Make sure the FastAPI server is running.', 'error');
    }
}

// Update status indicator
function updateStatus(text, status) {
    elements.statusText.textContent = text;
    elements.statusIndicator.className = `status-indicator ${status}`;
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const websiteUrl = elements.websiteUrlInput.value.trim();
    if (!websiteUrl) {
        showToast('Please enter a valid URL', 'error');
        return;
    }
    
    // Validate URL
    try {
        new URL(websiteUrl);
    } catch (error) {
        showToast('Please enter a valid URL', 'error');
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/fetch-insights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ website_url: websiteUrl })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            currentResults = data.data;
            displayResults(data.data);
            showToast('Insights fetched successfully!', 'success');
        } else {
            throw new Error(data.detail || data.error || 'Failed to fetch insights');
        }
    } catch (error) {
        console.error('Error fetching insights:', error);
        showError(error.message);
        showToast('Failed to fetch insights. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Show loading state
function showLoading() {
    elements.loadingSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
    elements.fetchBtn.disabled = true;
    elements.fetchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Fetching...</span>';
}

// Hide loading state
function hideLoading() {
    elements.loadingSection.style.display = 'none';
    elements.fetchBtn.disabled = false;
    elements.fetchBtn.innerHTML = '<i class="fas fa-download"></i><span>Fetch Insights</span>';
}

// Display results
function displayResults(data) {
    elements.resultsSection.style.display = 'block';
    elements.errorSection.style.display = 'none';
    
    // Generate summary cards
    generateSummaryCards(data);
    
    // Generate detailed content
    generateOverviewContent(data);
    generateProductsContent(data);
    generatePoliciesContent(data);
    generateFaqsContent(data);
    generateContactContent(data);
    generateSocialContent(data);
    generateLlmContent(data);
    generateRawJson(data);
    
    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

    // Generate summary cards
    function generateSummaryCards(data) {
        const summaryData = [
            { icon: 'fas fa-box', title: 'Products', value: data.products?.length || 0 },
            { icon: 'fas fa-star', title: 'Hero Products', value: data.hero_products?.length || 0 },
            { icon: 'fas fa-question-circle', title: 'FAQs', value: data.faqs?.length || 0 },
            { icon: 'fas fa-share-alt', title: 'Social Handles', value: Object.keys(data.social_handles || {}).length },
            { icon: 'fas fa-envelope', title: 'Contact Info', value: data.contact_details?.emails ? 'Yes' : 'No' },
            { icon: 'fas fa-file-contract', title: 'Policies', value: (data.privacy_policy || data.return_refund_policy) ? 'Yes' : 'No' },
            { icon: 'fas fa-brain', title: 'LLM Enhanced', value: data.insights_summary ? 'Yes' : 'No' }
        ];
    
    elements.summaryCards.innerHTML = summaryData.map(item => `
        <div class="summary-card">
            <i class="${item.icon}"></i>
            <h4>${item.title}</h4>
            <p>${item.value}</p>
        </div>
    `).join('');
}

// Generate overview content
function generateOverviewContent(data) {
    const overview = `
        <div class="overview-grid">
            <div class="overview-item">
                <h4><i class="fas fa-globe"></i> Store Information</h4>
                <p><strong>URL:</strong> ${data.store_url || 'N/A'}</p>
                <p><strong>Brand Context:</strong> ${data.brand_context || 'Not available'}</p>
            </div>
            
            <div class="overview-item">
                <h4><i class="fas fa-link"></i> Important Links</h4>
                ${Object.entries(data.important_links || {}).map(([key, value]) => 
                    `<p><strong>${key.replace(/_/g, ' ').toUpperCase()}:</strong> <a href="${value}" target="_blank">${value}</a></p>`
                ).join('') || '<p>No important links found</p>'}
            </div>
            
            <div class="overview-item">
                <h4><i class="fas fa-info-circle"></i> Metadata</h4>
                ${Object.entries(data.metadata || {}).slice(0, 5).map(([key, value]) => 
                    `<p><strong>${key}:</strong> ${value}</p>`
                ).join('') || '<p>No metadata available</p>'}
            </div>
        </div>
    `;
    
    elements.overviewContent.innerHTML = overview;
}

// Generate products content
function generateProductsContent(data) {
    const products = data.products || [];
    
    if (products.length === 0) {
        elements.productsContent.innerHTML = '<p>No products found.</p>';
        return;
    }
    
    const productsHtml = products.map(product => `
        <div class="product-card">
            <h4>${product.title || 'Untitled Product'}</h4>
            <div class="product-info">
                <div class="info-item">
                    <span class="info-label">Price</span>
                    <span class="info-value">${product.variants?.[0]?.price || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Vendor</span>
                    <span class="info-value">${product.vendor || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Type</span>
                    <span class="info-value">${product.product_type || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Available</span>
                    <span class="info-value">${product.variants?.[0]?.available ? 'Yes' : 'No'}</span>
                </div>
            </div>
            ${product.description ? `<p class="product-description">${product.description.substring(0, 200)}...</p>` : ''}
        </div>
    `).join('');
    
    elements.productsContent.innerHTML = productsHtml;
}

// Generate policies content
function generatePoliciesContent(data) {
    const policies = [];
    
    if (data.privacy_policy) {
        policies.push({
            title: 'Privacy Policy',
            content: data.privacy_policy,
            icon: 'fas fa-shield-alt'
        });
    }
    
    if (data.return_refund_policy) {
        policies.push({
            title: 'Return & Refund Policy',
            content: data.return_refund_policy,
            icon: 'fas fa-undo'
        });
    }
    
    if (policies.length === 0) {
        elements.policiesContent.innerHTML = '<p>No policies found.</p>';
        return;
    }
    
    const policiesHtml = policies.map(policy => `
        <div class="policy-card">
            <h4><i class="${policy.icon}"></i> ${policy.title}</h4>
            <div class="policy-content">
                ${policy.content.substring(0, 500)}${policy.content.length > 500 ? '...' : ''}
            </div>
        </div>
    `).join('');
    
    elements.policiesContent.innerHTML = policiesHtml;
}

// Generate FAQs content
function generateFaqsContent(data) {
    const faqs = data.faqs || [];
    
    if (faqs.length === 0) {
        elements.faqsContent.innerHTML = '<p>No FAQs found.</p>';
        return;
    }
    
    const faqsHtml = faqs.map(faq => `
        <div class="faq-item">
            <div class="faq-question">${faq.question || 'Question not available'}</div>
            <div class="faq-answer">${faq.answer || 'Answer not available'}</div>
        </div>
    `).join('');
    
    elements.faqsContent.innerHTML = faqsHtml;
}

// Generate contact content
function generateContactContent(data) {
    const contact = data.contact_details || {};
    
    const contactItems = [
        { icon: 'fas fa-envelope', title: 'Email Addresses', content: contact.emails || 'Not available' },
        { icon: 'fas fa-phone', title: 'Phone Numbers', content: contact.phone_numbers || 'Not available' },
        { icon: 'fas fa-map-marker-alt', title: 'Address', content: contact.address || 'Not available' },
        { icon: 'fas fa-link', title: 'Social Links', content: contact.social_links || 'Not available' }
    ];
    
    const contactHtml = `
        <div class="contact-grid">
            ${contactItems.map(item => `
                <div class="contact-item">
                    <h4><i class="${item.icon}"></i> ${item.title}</h4>
                    <p>${item.content}</p>
                </div>
            `).join('')}
        </div>
    `;
    
    elements.contactContent.innerHTML = contactHtml;
}

// Generate social content
function generateSocialContent(data) {
    const socialHandles = data.social_handles || {};
    
    if (Object.keys(socialHandles).length === 0) {
        elements.socialContent.innerHTML = '<p>No social media handles found.</p>';
        return;
    }
    
    const socialPlatforms = {
        instagram: { icon: 'fab fa-instagram', name: 'Instagram' },
        facebook: { icon: 'fab fa-facebook', name: 'Facebook' },
        twitter: { icon: 'fab fa-twitter', name: 'Twitter' },
        youtube: { icon: 'fab fa-youtube', name: 'YouTube' },
        tiktok: { icon: 'fab fa-tiktok', name: 'TikTok' },
        linkedin: { icon: 'fab fa-linkedin', name: 'LinkedIn' },
        pinterest: { icon: 'fab fa-pinterest', name: 'Pinterest' },
        snapchat: { icon: 'fab fa-snapchat', name: 'Snapchat' },
        whatsapp: { icon: 'fab fa-whatsapp', name: 'WhatsApp' }
    };
    
    const socialHtml = `
        <div class="social-grid">
            ${Object.entries(socialHandles).map(([platform, handle]) => {
                const platformInfo = socialPlatforms[platform] || { icon: 'fas fa-share', name: platform };
                return `
                    <div class="social-item ${platform}">
                        <i class="${platformInfo.icon}"></i>
                        <h4>${platformInfo.name}</h4>
                        <p>${handle || 'Not available'}</p>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    elements.socialContent.innerHTML = socialHtml;
}

// Generate LLM insights content
function generateLlmContent(data) {
    const llmData = {
        insights_summary: data.insights_summary,
        product_analysis: data.product_analysis,
        social_analysis: data.social_analysis
    };
    
    if (!llmData.insights_summary && !llmData.product_analysis && !llmData.social_analysis) {
        elements.llmContent.innerHTML = '<p>No LLM-enhanced insights available. Make sure to set up your GEMINI_API_KEY environment variable.</p>';
        return;
    }
    
    const llmHtml = `
        <div class="llm-insights">
            ${llmData.insights_summary ? `
                <div class="llm-section">
                    <h4><i class="fas fa-chart-line"></i> AI-Generated Summary</h4>
                    <div class="llm-content-box">
                        <p>${llmData.insights_summary}</p>
                    </div>
                </div>
            ` : ''}
            
            ${llmData.product_analysis?.analysis ? `
                <div class="llm-section">
                    <h4><i class="fas fa-boxes"></i> Product Analysis</h4>
                    <div class="llm-content-box">
                        <p>${llmData.product_analysis.analysis}</p>
                        ${llmData.product_analysis.categories ? `
                            <div class="categories-grid">
                                <h5>Product Categories:</h5>
                                <div class="category-items">
                                    ${Object.entries(llmData.product_analysis.categories).map(([category, count]) => 
                                        `<span class="category-tag">${category}: ${count}</span>`
                                    ).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${llmData.social_analysis?.analysis ? `
                <div class="llm-section">
                    <h4><i class="fas fa-share-alt"></i> Social Media Analysis</h4>
                    <div class="llm-content-box">
                        <p>${llmData.social_analysis.analysis}</p>
                        ${llmData.social_analysis.recommendations?.length ? `
                            <div class="recommendations">
                                <h5>Recommendations:</h5>
                                <ul>
                                    ${llmData.social_analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    
    elements.llmContent.innerHTML = llmHtml;
}

// Generate raw JSON content
function generateRawJson(data) {
    elements.rawJson.textContent = JSON.stringify(data, null, 2);
}

// Switch tabs
function switchTab(tabName) {
    // Remove active class from all tabs and panes
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    // Add active class to selected tab and pane
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// Show error
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';
    elements.loadingSection.style.display = 'none';
}

// Hide error
function hideError() {
    elements.errorSection.style.display = 'none';
}

// Clear results
function clearResults() {
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
    elements.websiteUrlInput.value = '';
    currentResults = null;
    showToast('Results cleared', 'info');
}

// Export results
function exportResults() {
    if (!currentResults) {
        showToast('No results to export', 'error');
        return;
    }
    
    const dataStr = JSON.stringify(currentResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'shopify-insights.json';
    link.click();
    
    URL.revokeObjectURL(url);
    showToast('Results exported successfully!', 'success');
}

// Copy results
async function copyResults() {
    if (!currentResults) {
        showToast('No results to copy', 'error');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(JSON.stringify(currentResults, null, 2));
        showToast('Results copied to clipboard!', 'success');
    } catch (error) {
        showToast('Failed to copy results', 'error');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                 type === 'error' ? 'fas fa-exclamation-circle' : 
                 'fas fa-info-circle';
    
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Add some CSS for the overview grid
const style = document.createElement('style');
style.textContent = `
    .overview-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
    }
    
    .overview-item {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .overview-item h4 {
        font-size: 1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .overview-item p {
        margin-bottom: 0.5rem;
        color: #666;
    }
    
    .overview-item a {
        color: #667eea;
        text-decoration: none;
    }
    
    .overview-item a:hover {
        text-decoration: underline;
    }
    
    .policy-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .policy-card h4 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .policy-content {
        color: #666;
        line-height: 1.6;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .product-description {
        margin-top: 1rem;
        color: #666;
        font-style: italic;
    }
`;
document.head.appendChild(style);
