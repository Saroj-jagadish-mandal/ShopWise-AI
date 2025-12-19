import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  MessageSquare, 
  Bot, 
  User, 
  ShoppingCart,
  Package,
  Loader2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './ChatWindow.css';

const ChatWindow = ({ 
  selectedProduct, 
  messages, 
  onSendMessage, 
  isLoading 
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedProduct) {
      inputRef.current?.focus();
    }
  }, [selectedProduct]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Welcome State - No product selected
  if (!selectedProduct) {
    return (
      <div className="chat-window">
        <div className="welcome-container">
          <div className="welcome-content">
            <div className="welcome-icon">
              <ShoppingCart size={64} />
            </div>
            <h1 className="welcome-title">
              <span className="gradient-text">Welcome to ShopWise AI</span>
            </h1>
            <p className="welcome-subtitle">
              Your intelligent shopping assistant powered by AI
            </p>
            <div className="welcome-steps">
              <div className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>Add a Product</h4>
                  <p>Paste an Amazon product URL in the sidebar</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Wait for Processing</h4>
                  <p>We'll analyze reviews and product details</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>Ask Anything</h4>
                  <p>Get instant, accurate answers about the product</p>
                </div>
              </div>
            </div>
            <div className="welcome-features">
              <div className="feature">
                <MessageSquare size={20} />
                <span>Natural Conversations</span>
              </div>
              <div className="feature">
                <Bot size={20} />
                <span>AI-Powered Insights</span>
              </div>
              <div className="feature">
                <Package size={20} />
                <span>Review Analysis</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {/* Chat Header */}
      <div className="chat-header glass">
        <div className="chat-product-info">
          <div className="chat-product-image">
            {selectedProduct.image_url ? (
              <img src={selectedProduct.image_url} alt={selectedProduct.title} />
            ) : (
              <Package size={24} />
            )}
          </div>
          <div className="chat-product-details">
            <h3 className="chat-product-title">{selectedProduct.title}</h3>
            {selectedProduct.brand && (
              <span className="chat-product-brand">by {selectedProduct.brand}</span>
            )}
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Bot size={48} className="empty-bot-icon" />
            <h3>Start a Conversation</h3>
            <p>Ask me anything about this product!</p>
            <div className="suggestion-chips">
              <button 
                className="chip" 
                onClick={() => setInput("What are the main pros and cons?")}
              >
                Pros and Cons?
              </button>
              <button 
                className="chip"
                onClick={() => setInput("Is this product worth buying?")}
              >
                Worth buying?
              </button>
              <button 
                className="chip"
                onClick={() => setInput("What do reviewers say about quality?")}
              >
                Quality reviews?
              </button>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`message ${message.role}`}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? (
                    <User size={20} />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                <div className="message-content">
                  {message.role === 'assistant' ? (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  ) : (
                    <p>{message.content}</p>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">
                  <Bot size={20} />
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="chat-form">
          <div className="input-wrapper glass">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about this product..."
              className="chat-input"
              rows={1}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? (
                <Loader2 size={20} className="spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
          <p className="input-hint">
            Press Enter to send, Shift + Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;
