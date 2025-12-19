import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar/Navbar';
import Sidebar from './components/Sidebar/Sidebar';
import ChatWindow from './components/ChatWindow/ChatWindow';
import { 
  getProducts, 
  addProduct, 
  deleteProduct, 
  retryProduct,
  askQuestion,
  pollProductStatus 
} from './services/api';
import './App.css';

function App() {
  // Theme State
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('shopwise-theme');
    return savedTheme || 'dark';
  });

  // UI State
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  // Data State
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  
  // Loading States
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('shopwise-theme', theme);
  }, [theme]);

  // Fetch products on mount
  useEffect(() => {
    fetchProducts();
  }, []);

  const handleToggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const fetchProducts = async () => {
    setIsLoadingProducts(true);
    try {
      const response = await getProducts();
      // Handle paginated response
      const productList = response.results || response;
      setProducts(productList);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  const handleToggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleAddProduct = async (url) => {
    try {
      const response = await addProduct(url);
      const newProduct = response.product;
      
      // Add to products list
      setProducts(prev => [newProduct, ...prev]);
      
      // If product needs processing, poll for status
      if (newProduct.status !== 'completed') {
        pollProductStatus(newProduct.id, (status) => {
          setProducts(prev => 
            prev.map(p => 
              p.id === newProduct.id 
                ? { ...p, status: status.status, error_message: status.error_message }
                : p
            )
          );
          
          // Refresh product data when completed
          if (status.status === 'completed') {
            fetchProducts();
          }
        });
      }
      
      return newProduct;
    } catch (error) {
      console.error('Failed to add product:', error);
      throw error;
    }
  };

  const handleDeleteProduct = async (productId) => {
    try {
      await deleteProduct(productId);
      setProducts(prev => prev.filter(p => p.id !== productId));
      
      // Clear selection if deleted product was selected
      if (selectedProduct?.id === productId) {
        setSelectedProduct(null);
        setMessages([]);
        setSessionId(null);
      }
    } catch (error) {
      console.error('Failed to delete product:', error);
    }
  };

  const handleRetryProduct = async (productId) => {
    try {
      await retryProduct(productId);
      
      // Update product status to pending
      setProducts(prev => 
        prev.map(p => 
          p.id === productId 
            ? { ...p, status: 'pending', error_message: null }
            : p
        )
      );
      
      // Poll for status updates
      pollProductStatus(productId, (status) => {
        setProducts(prev => 
          prev.map(p => 
            p.id === productId 
              ? { ...p, status: status.status, error_message: status.error_message }
              : p
          )
        );
        
        if (status.status === 'completed') {
          fetchProducts();
        }
      });
    } catch (error) {
      console.error('Failed to retry product:', error);
    }
  };

  const handleSelectProduct = useCallback((product) => {
    setSelectedProduct(product);
    setMessages([]);
    setSessionId(null);
  }, []);

  const handleSendMessage = async (question) => {
    if (!selectedProduct) return;
    
    // Add user message immediately
    const userMessage = { role: 'user', content: question };
    setMessages(prev => [...prev, userMessage]);
    setIsSendingMessage(true);
    
    try {
      const response = await askQuestion(selectedProduct.id, question, sessionId);
      
      // Save session ID for conversation continuity
      if (response.session_id) {
        setSessionId(response.session_id);
      }
      
      // Add assistant response
      const assistantMessage = { 
        role: 'assistant', 
        content: response.answer,
        context_chunks: response.context_chunks 
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your question. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSendingMessage(false);
    }
  };

  return (
    <div className="app" data-theme={theme}>
      <Navbar 
        onToggleSidebar={handleToggleSidebar} 
        isSidebarOpen={isSidebarOpen}
        theme={theme}
        onToggleTheme={handleToggleTheme}
      />
      
      <div className="app-container">
        <Sidebar
          isOpen={isSidebarOpen}
          products={products}
          selectedProduct={selectedProduct}
          onSelectProduct={handleSelectProduct}
          onAddProduct={handleAddProduct}
          onDeleteProduct={handleDeleteProduct}
          onRetryProduct={handleRetryProduct}
          isLoading={isLoadingProducts}
        />
        
        <main className={`main-content ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          <ChatWindow
            selectedProduct={selectedProduct}
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isSendingMessage}
          />
        </main>
      </div>
    </div>
  );
}

export default App;
