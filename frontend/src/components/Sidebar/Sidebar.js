import React, { useState } from 'react';
import { 
  Link2, 
  Plus, 
  Package, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Trash2,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ 
  isOpen, 
  products, 
  selectedProduct, 
  onSelectProduct, 
  onAddProduct,
  onDeleteProduct,
  onRetryProduct,
  isLoading 
}) => {
  const [url, setUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    
    setIsSubmitting(true);
    try {
      await onAddProduct(url.trim());
      setUrl('');
    } catch (error) {
      console.error('Failed to add product:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="status-icon status-completed" />;
      case 'pending':
      case 'scraping':
      case 'embedding':
        return <Loader2 size={16} className="status-icon status-pending" />;
      case 'failed':
        return <AlertCircle size={16} className="status-icon status-failed" />;
      default:
        return <Clock size={16} className="status-icon" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Ready';
      case 'pending':
        return 'Pending...';
      case 'scraping':
        return 'Scraping...';
      case 'embedding':
        return 'Processing...';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  const truncateTitle = (title, maxLength = 50) => {
    if (!title) return 'Untitled Product';
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength) + '...';
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-content">
        {/* URL Input Section */}
        <div className="sidebar-section url-section">
          <div className="section-header">
            <Link2 size={18} />
            <h3>Add Product</h3>
          </div>
          <form onSubmit={handleSubmit} className="url-form">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste Amazon product URL..."
              className="url-input"
              disabled={isSubmitting}
            />
            <button 
              type="submit" 
              className="btn btn-primary add-btn"
              disabled={isSubmitting || !url.trim()}
            >
              {isSubmitting ? (
                <Loader2 size={18} className="spin" />
              ) : (
                <Plus size={18} />
              )}
              <span>{isSubmitting ? 'Adding...' : 'Add'}</span>
            </button>
          </form>
        </div>

        {/* Products List Section */}
        <div className="sidebar-section products-section">
          <div className="section-header">
            <Package size={18} />
            <h3>Your Products</h3>
            <span className="product-count">{products.length}</span>
          </div>
          
          <div className="products-list">
            {isLoading ? (
              <div className="loading-state">
                <Loader2 size={24} className="spin" />
                <span>Loading products...</span>
              </div>
            ) : products.length === 0 ? (
              <div className="empty-state">
                <Package size={48} className="empty-icon" />
                <p>No products yet</p>
                <span>Paste an Amazon URL above to get started</span>
              </div>
            ) : (
              products.map((product) => (
                <div
                  key={product.id}
                  className={`product-card ${selectedProduct?.id === product.id ? 'selected' : ''}`}
                  onClick={() => product.status === 'completed' && onSelectProduct(product)}
                >
                  <div className="product-image">
                    {product.image_url ? (
                      <img src={product.image_url} alt={product.title} />
                    ) : (
                      <Package size={24} />
                    )}
                  </div>
                  <div className="product-info">
                    <h4 className="product-title">{truncateTitle(product.title)}</h4>
                    <div className="product-meta">
                      {getStatusIcon(product.status)}
                      <span className={`status-text status-${product.status}`}>
                        {getStatusText(product.status)}
                      </span>
                    </div>
                    {product.brand && (
                      <span className="product-brand">{product.brand}</span>
                    )}
                  </div>
                  <div className="product-actions">
                    {product.status === 'failed' && (
                      <button
                        className="action-btn retry-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onRetryProduct(product.id);
                        }}
                        title="Retry"
                      >
                        <RefreshCw size={14} />
                      </button>
                    )}
                    {product.url && (
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="action-btn"
                        onClick={(e) => e.stopPropagation()}
                        title="View on Amazon"
                      >
                        <ExternalLink size={14} />
                      </a>
                    )}
                    <button
                      className="action-btn delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteProduct(product.id);
                      }}
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
