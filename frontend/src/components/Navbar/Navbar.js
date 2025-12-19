import React from 'react';
import { Menu, Sun, Moon } from 'lucide-react';
import './Navbar.css';

const Navbar = ({ onToggleSidebar, isSidebarOpen, theme, onToggleTheme }) => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <button 
          className="sidebar-toggle"
          onClick={onToggleSidebar}
          aria-label={isSidebarOpen ? 'Close sidebar' : 'Open sidebar'}
        >
          <Menu size={20} />
        </button>
        
        <div className="logo">
          <div className="logo-text">
            <span className="logo-name">ShopWise</span>
            <span className="logo-suffix">AI</span>
          </div>
        </div>
      </div>
      
      <div className="navbar-right">
        <button 
          className="theme-toggle"
          onClick={onToggleTheme}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        
        <div className="nav-status">
          <span className="status-dot"></span>
          <span className="status-text">Ready</span>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
