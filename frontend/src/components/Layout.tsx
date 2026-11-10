// src/components/Layout.tsx
import React from 'react';
import { useLocation } from 'react-router-dom';
import { Nav } from './Nav';
import { Footer } from './Footer';

export interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const isAuthPage = location.pathname === '/login';

  return (
    <div className="min-h-screen flex flex-col bg-secondary text-ink grain-surface">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:bg-ink focus:text-ink-light focus:px-4 focus:py-2 focus:rounded-button focus:font-mono focus:text-terminal"
      >
        Skip to content
      </a>

      {!isAuthPage && <Nav />}

      <main id="main-content" className="flex-1 flex flex-col">
        {children}
      </main>

      <Footer />
    </div>
  );
};

export default Layout;