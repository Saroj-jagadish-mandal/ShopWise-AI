import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`📡 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status}`);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ===== Product API Methods =====

/**
 * Get all products with optional filtering
 * @param {Object} params - Query parameters (search, status, page)
 */
export const getProducts = async (params = {}) => {
  const response = await api.get('/products/', { params });
  return response.data;
};

/**
 * Get a single product by ID
 * @param {string} productId - Product UUID
 */
export const getProduct = async (productId) => {
  const response = await api.get(`/products/${productId}/`);
  return response.data;
};

/**
 * Add a new product by URL (initiates scraping)
 * @param {string} url - Amazon product URL
 */
export const addProduct = async (url) => {
  const response = await api.post('/products/', { url });
  return response.data;
};

/**
 * Get product status (for polling during scraping)
 * @param {string} productId - Product UUID
 */
export const getProductStatus = async (productId) => {
  const response = await api.get(`/products/${productId}/status/`);
  return response.data;
};

/**
 * Delete a product
 * @param {string} productId - Product UUID
 */
export const deleteProduct = async (productId) => {
  const response = await api.delete(`/products/${productId}/`);
  return response.data;
};

/**
 * Retry a failed product scraping
 * @param {string} productId - Product UUID
 */
export const retryProduct = async (productId) => {
  const response = await api.post(`/products/${productId}/retry/`);
  return response.data;
};

// ===== Chat API Methods =====

/**
 * Ask a question about a product
 * @param {string} productId - Product UUID
 * @param {string} question - User's question
 * @param {string} sessionId - Optional chat session ID for context
 */
export const askQuestion = async (productId, question, sessionId = null) => {
  const payload = { question };
  if (sessionId) {
    payload.session_id = sessionId;
  }
  const response = await api.post(`/products/${productId}/ask/`, payload);
  return response.data;
};

/**
 * Get all chat sessions for a product
 * @param {string} productId - Product UUID
 */
export const getChatSessions = async (productId) => {
  const response = await api.get(`/products/${productId}/chat-sessions/`);
  return response.data;
};

/**
 * Get messages for a specific chat session
 * @param {string} sessionId - Chat session ID
 */
export const getChatMessages = async (sessionId) => {
  const response = await api.get(`/chat-sessions/${sessionId}/messages/`);
  return response.data;
};

// ===== Utility Methods =====

/**
 * Poll product status until completion or failure
 * @param {string} productId - Product UUID
 * @param {function} onStatusUpdate - Callback for status updates
 * @param {number} interval - Polling interval in ms (default: 2000)
 */
export const pollProductStatus = (productId, onStatusUpdate, interval = 2000) => {
  const pollInterval = setInterval(async () => {
    try {
      const status = await getProductStatus(productId);
      onStatusUpdate(status);
      
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(pollInterval);
      }
    } catch (error) {
      console.error('Polling error:', error);
      clearInterval(pollInterval);
      onStatusUpdate({ status: 'failed', error: error.message });
    }
  }, interval);
  
  return () => clearInterval(pollInterval);
};

export default api;
