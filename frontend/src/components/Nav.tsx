// src/components/Nav.tsx
import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../assets/GoodladTwinstars_logo.svg';
import { Button } from './Button';

export const Nav: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 12);
    };
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname, location.hash]);

  const isPricingActive = location.pathname === '/pricing';
  const isProductActive = location.pathname === '/' && location.hash === '#product';
  const isEnterpriseActive = location.pathname === '/' && location.hash === '#enterprise';

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-colors duration-300 ${
        isScrolled || mobileMenuOpen
          ? 'glass-panel shadow-glass'
          : 'bg-transparent border-b border-transparent'
      }`}
    >
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Left: Official Goodlad Twinstars Logo */}
        <Link
          to="/"
          aria-label="Goodlad Twinstars — DocugraphAI Home"
          className="inline-flex items-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ink"
        >
          <img
            src={logo}
            alt="Goodlad Twinstars"
            className="h-[30px] md:h-[36px] w-auto block"
          />
        </Link>

        {/* Right: Desktop Navigation Links + CTA */}
        <nav aria-label="Primary navigation" className="hidden md:flex items-center gap-8">
          <Link
            to="/#product"
            aria-current={isProductActive ? 'page' : undefined}
            className={`font-heading text-small font-medium py-1 border-b-2 transition-colors ${
              isProductActive
                ? 'border-accent text-ink'
                : 'border-transparent text-ink-secondary hover:text-ink hover:border-accent/60'
            }`}
          >
            Product
          </Link>

          <Link
            to="/#enterprise"
            aria-current={isEnterpriseActive ? 'page' : undefined}
            className={`font-heading text-small font-medium py-1 border-b-2 transition-colors ${
              isEnterpriseActive
                ? 'border-accent text-ink'
                : 'border-transparent text-ink-secondary hover:text-ink hover:border-accent/60'
            }`}
          >
            Enterprise
          </Link>

          <Link
            to="/pricing"
            aria-current={isPricingActive ? 'page' : undefined}
            className={`font-heading text-small font-medium py-1 border-b-2 transition-colors ${
              isPricingActive
                ? 'border-accent text-ink'
                : 'border-transparent text-ink-secondary hover:text-ink hover:border-accent/60'
            }`}
          >
            Pricing
          </Link>

          <a
            href="#"
            title="Coming soon"
            onClick={(e) => e.preventDefault()}
            className="font-heading text-small font-medium py-1 border-b-2 border-transparent text-ink-secondary hover:text-ink inline-flex items-center gap-1.5 cursor-help"
          >
            <span>Docs</span>
            <span className="font-mono text-[0.65rem] uppercase tracking-[0.02em] px-1.5 py-0.5 bg-ink/10 text-ink rounded-button">
              Soon
            </span>
          </a>

          <Button to="/login#request-access" variant="primary">
            Request org access
          </Button>
        </nav>

        {/* Mobile Menu Button */}
        <button
          type="button"
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-primary-menu"
          aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          onClick={() => setMobileMenuOpen((prev) => !prev)}
          className="md:hidden inline-flex items-center justify-center p-2 rounded-button border border-ink/20 text-ink hover:bg-primary/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ink"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 22 22"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            {mobileMenuOpen ? (
              <>
                <line x1="4" y1="4" x2="18" y2="18" stroke="currentColor" strokeWidth="1.75" />
                <line x1="18" y1="4" x2="4" y2="18" stroke="currentColor" strokeWidth="1.75" />
              </>
            ) : (
              <>
                <line x1="3" y1="6" x2="19" y2="6" stroke="currentColor" strokeWidth="1.75" />
                <line x1="3" y1="11" x2="19" y2="11" stroke="currentColor" strokeWidth="1.75" />
                <line x1="3" y1="16" x2="14" y2="16" stroke="currentColor" strokeWidth="1.75" />
              </>
            )}
          </svg>
        </button>
      </div>

      {/* Collapsible Mobile Drawer */}
      {mobileMenuOpen && (
        <nav
          id="mobile-primary-menu"
          aria-label="Mobile navigation"
          className="md:hidden glass-panel border-t border-primary/30 px-4 pt-3 pb-6"
        >
          <div className="flex flex-col gap-3">
            <Link
              to="/#product"
              aria-current={isProductActive ? 'page' : undefined}
              className={`font-heading text-body font-medium py-2 border-l-2 pl-3 ${
                isProductActive ? 'border-accent text-ink' : 'border-transparent text-ink-secondary'
              }`}
            >
              Product
            </Link>
            <Link
              to="/#enterprise"
              aria-current={isEnterpriseActive ? 'page' : undefined}
              className={`font-heading text-body font-medium py-2 border-l-2 pl-3 ${
                isEnterpriseActive ? 'border-accent text-ink' : 'border-transparent text-ink-secondary'
              }`}
            >
              Enterprise
            </Link>
            <Link
              to="/pricing"
              aria-current={isPricingActive ? 'page' : undefined}
              className={`font-heading text-body font-medium py-2 border-l-2 pl-3 ${
                isPricingActive ? 'border-accent text-ink' : 'border-transparent text-ink-secondary'
              }`}
            >
              Pricing
            </Link>
            <a
              href="#"
              title="Coming soon"
              onClick={(e) => e.preventDefault()}
              className="font-heading text-body font-medium py-2 border-l-2 border-transparent pl-3 text-ink-secondary flex items-center justify-between"
            >
              <span>Docs</span>
              <span className="font-mono text-terminal uppercase tracking-[0.02em] px-2 py-0.5 bg-ink text-accent rounded-button">
                Coming soon
              </span>
            </a>
            <div className="pt-2">
              <Button to="/login#request-access" variant="primary" className="w-full">
                Request org access
              </Button>
            </div>
          </div>
        </nav>
      )}
    </header>
  );
};

export default Nav;