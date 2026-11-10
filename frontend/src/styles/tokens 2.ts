export const BRAND_TOKENS = {
  colors: {
    primary: 'var(--color-primary)',
    secondary: 'var(--color-secondary)',
    accent: 'var(--color-accent)',
    ink: 'var(--color-ink)',
    inkSecondary: 'var(--color-ink-secondary)',
    inkLight: 'var(--color-ink-light)',
  },
  fonts: {
    heading: 'var(--font-heading)',
    body: 'var(--font-body)',
    mono: 'var(--font-mono)',
  },
  radii: {
    sharp: 'var(--radius-sharp)',
    card: 'var(--radius-card)',
    button: 'var(--radius-button)',
  },
  layout: {
    maxWidthLanding: '1200px',
    maxWidthAuth: '960px',
    sectionPaddingDesktop: '80px',
    sectionPaddingMobile: '48px',
    cardPadding: '32px',
    gridGutter: '24px',
    cardGap: '16px',
  },
} as const;
CSS
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: #8DB9F0;
  --color-secondary: #E9E8F8;
  --color-accent: #F5B69E;
  --color-ink: #101828;
  --color-ink-secondary: #2C3E50;
  --color-ink-light: #E9E8F8;
  --font-heading: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --radius-sharp: 0px;
  --radius-card: 8px;
  --radius-button: 4px;
  --shadow-glass: 0 4px 30px rgba(0, 0, 0, 0.1);
  --blur-glass: blur(12px);

  /* Functional alpha surfaces derived from the palette tokens */
  --surface-glass-bg: rgba(233, 232, 248, 0.6);
  --surface-glass-border: rgba(141, 185, 240, 0.3);
  --surface-ink-subtle: rgba(16, 24, 40, 0.12);
  --surface-ink-border: rgba(16, 24, 40, 0.2);
  --surface-accent-border: rgba(245, 182, 158, 0.3);
  --shadow-accent-glow: 0 0 18px rgba(245, 182, 158, 0.45);
  --scanline-stripe: rgba(233, 232, 248, 0.03);
  --scanline-ink-stripe: rgba(16, 24, 40, 0.03);
  --ink-light-60: rgba(233, 232, 248, 0.6);
  --ink-light-40: rgba(233, 232, 248, 0.4);
}

@layer base {
  html {
    font-family: var(--font-body);
    color: var(--color-ink);
    background-color: var(--color-secondary);
    scroll-behavior: smooth;
  }

  body {
    margin: 0;
    min-height: 100vh;
    background-color: var(--color-secondary);
    color: var(--color-ink);
    overflow-x: hidden;
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    font-family: var(--font-heading);
    color: var(--color-ink);
    letter-spacing: -0.03em;
  }

  h1 {
    font-size: 2.5rem;
    line-height: 1.1;
    letter-spacing: -0.035em;
    font-weight: 700;
  }

  h2 {
    font-size: 2rem;
    line-height: 1.15;
    letter-spacing: -0.025em;
    font-weight: 600;
  }

  h3 {
    font-size: 1.5rem;
    line-height: 1.25;
    letter-spacing: -0.02em;
    font-weight: 600;
  }

  @media (min-width: 768px) {
    h1 {
      font-size: 3.5rem;
    }
    h2 {
      font-size: 2.5rem;
    }
    h3 {
      font-size: 1.75rem;
    }
  }

  code,
  pre {
    font-family: var(--font-mono);
    letter-spacing: 0.02em;
  }

  :focus-visible {
    outline: 2px solid var(--color-ink);
    outline-offset: 2px;
  }
}

/* Subtle analog SVG grain overlay (2.5% opacity) */
.grain-surface {
  position: relative;
}

.grain-surface::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 40;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

/* Atmospheric directional washes (never 90deg horizontal) */
@keyframes atmosphericShift {
  0% {
    background-position: 0% 0%;
  }
  50% {
    background-position: 100% 100%;
  }
  100% {
    background-position: 0% 0%;
  }
}

.wash-atmospheric-135 {
  background: linear-gradient(
    135deg,
    var(--color-primary) 0%,
    var(--color-secondary) 62%,
    var(--color-accent) 100%
  );
  background-size: 200% 200%;
  animation: atmosphericShift 9s ease-in-out infinite;
}

.wash-atmospheric-225 {
  background: linear-gradient(
    225deg,
    var(--color-secondary) 0%,
    var(--color-primary) 65%,
    var(--color-accent) 100%
  );
  background-size: 200% 200%;
  animation: atmosphericShift 8s ease-in-out infinite;
}

.wash-atmospheric-180 {
  background: linear-gradient(
    180deg,
    var(--color-primary) 0%,
    var(--color-secondary) 100%
  );
}

/* Glassmorphism surfaces (used sparingly on floating cards and sticky nav) */
.glass-panel {
  background: var(--surface-glass-bg);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--surface-glass-border);
}

/* Retro-futuristic scan lines: 1px every 24px at 0.03 opacity */
.scanlines-dark {
  background-image: repeating-linear-gradient(
    180deg,
    var(--scanline-stripe) 0px,
    var(--scanline-stripe) 1px,
    transparent 1px,
    transparent 24px
  );
}

.scanlines-light {
  background-image: repeating-linear-gradient(
    180deg,
    var(--scanline-ink-stripe) 0px,
    var(--scanline-ink-stripe) 1px,
    transparent 1px,
    transparent 24px
  );
}

/* 12-column architectural grid helper */
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
}

/* Motion accessibility compliance */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  .wash-atmospheric-135,
  .wash-atmospheric-225 {
    animation: none !important;
  }
}
TypeScript
// src/components/Button.tsx
import React from 'react';
import { Link } from 'react-router-dom';

export type ButtonVariant = 'primary' | 'secondary';

interface BaseProps {
  variant?: ButtonVariant;
  children: React.ReactNode;
  className?: string;
}

type ButtonAsButton = BaseProps &
  Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, keyof BaseProps> & {
    to?: undefined;
    href?: undefined;
  };

type ButtonAsRouterLink = BaseProps &
  Omit<React.ComponentProps<typeof Link>, keyof BaseProps | 'to'> & {
    to: string;
    href?: undefined;
  };

type ButtonAsAnchor = BaseProps &
  Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, keyof BaseProps | 'href'> & {
    href: string;
    to?: undefined;
  };

export type ButtonProps = ButtonAsButton | ButtonAsRouterLink | ButtonAsAnchor;

export const Button: React.FC<ButtonProps> = (props) => {
  const { variant = 'primary', children, className = '' } = props;

  const baseStyles =
    'inline-flex items-center justify-center font-heading font-medium text-small px-5 py-2.5 rounded-button transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink select-none';

  const variantStyles: Record<ButtonVariant, string> = {
    primary:
      'bg-accent text-ink border border-ink/15 hover:shadow-accent-glow active:translate-y-[1px]',
    secondary:
      'bg-transparent text-ink border border-ink hover:bg-ink hover:text-ink-light active:translate-y-[1px]',
  };

  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className}`.trim();

  if ('to' in props && props.to !== undefined) {
    const { to, variant: _v, children: _c, className: _cn, ...linkRest } = props;
    return (
      <Link to={to} className={combinedClassName} {...linkRest}>
        {children}
      </Link>
    );
  }

  if ('href' in props && props.href !== undefined) {
    const { href, variant: _v, children: _c, className: _cn, ...anchorRest } = props;
    return (
      <a href={href} className={combinedClassName} {...anchorRest}>
        {children}
      </a>
    );
  }

  const { variant: _v, children: _c, className: _cn, ...buttonRest } = props as ButtonAsButton;
  return (
    <button type="button" className={combinedClassName} {...buttonRest}>
      {children}
    </button>
  );
};

export default Button;
TypeScript
// src/components/TerminalLabel.tsx
import React from 'react';

export interface TerminalLabelProps {
  children: React.ReactNode;
  className?: string;
  showIndicator?: boolean;
}

export const TerminalLabel: React.FC<TerminalLabelProps> = ({
  children,
  className = '',
  showIndicator = true,
}) => {
  return (
    <span
      className={`inline-flex items-center gap-2 bg-ink text-accent font-mono text-terminal uppercase tracking-[0.02em] px-2.5 py-1 rounded-button border border-primary/30 ${className}`.trim()}
    >
      {showIndicator && (
        <span
          aria-hidden="true"
          className="inline-block w-1.5 h-1.5 bg-accent rounded-sharp"
        />
      )}
      <span>{children}</span>
    </span>
  );
};

export default TerminalLabel;
TypeScript
// src/components/Divider.tsx
import React from 'react';

export interface DividerProps {
  className?: string;
  tone?: 'light' | 'dark';
}

export const Divider: React.FC<DividerProps> = ({ className = '', tone = 'light' }) => {
  const lineClass =
    tone === 'dark' ? 'border-ink-light/20' : 'border-ink/15';
  const nodeStrokeClass =
    tone === 'dark' ? 'text-accent' : 'text-ink-secondary';

  return (
    <div
      role="separator"
      aria-orientation="horizontal"
      className={`w-full flex items-center justify-center my-8 ${className}`.trim()}
    >
      <div className={`flex-1 border-t ${lineClass}`} />
      <div className={`mx-4 flex items-center gap-1.5 ${nodeStrokeClass}`} aria-hidden="true">
        <span className="inline-block w-1 h-1 bg-accent" />
        <svg
          width="14"
          height="14"
          viewBox="0 0 14 14"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="block"
        >
          <path
            d="M7 1L13 7L7 13L1 7L7 1Z"
            stroke="currentColor"
            strokeWidth="1.2"
          />
          <line x1="7" y1="0" x2="7" y2="14" stroke="currentColor" strokeWidth="0.75" />
          <line x1="0" y1="7" x2="14" y2="7" stroke="currentColor" strokeWidth="0.75" />
        </svg>
        <span className="inline-block w-1 h-1 bg-accent" />
      </div>
      <div className={`flex-1 border-t ${lineClass}`} />
    </div>
  );
};

export default Divider;
TypeScript
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
TypeScript
// src/components/Footer.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../assets/GoodladTwinstars_logo.svg';

const FOOTER_LINKS = [
  { label: 'Home', to: '/' },
  { label: 'Login', to: '/login' },
  { label: 'Pricing', to: '/pricing' },
  { label: 'Terms', to: '/terms' },
  { label: 'Privacy', to: '/privacy' },
] as const;

export const Footer: React.FC = () => {
  const location = useLocation();

  return (
    <footer
      className="bg-ink text-ink-light scanlines-dark border-b border-accent/30"
      style={{ borderBottomColor: 'var(--surface-accent-border)' }}
    >
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8">
          {/* Left: Official Logo in Lavender Plate + Brand Nomenclature */}
          <div className="flex flex-col items-start gap-2.5">
            <Link
              to="/"
              aria-label="Goodlad Twinstars Home"
              className="inline-block bg-secondary p-[8px] rounded-button focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              <img
                src={logo}
                alt="Goodlad Twinstars"
                className="h-[28px] w-auto block"
              />
            </Link>
            <span className="font-heading text-[1rem] font-medium text-ink-light">
              Goodlad Twinstars
            </span>
            <p className="font-mono text-[0.75rem] tracking-[0.02em] text-primary m-0">
              DocugraphAI — A Hybrid GraphRAG Document Intelligence Engine
            </p>
          </div>

          {/* Center: Route Navigation */}
          <nav aria-label="Footer navigation" className="flex flex-wrap items-center gap-y-2">
            {FOOTER_LINKS.map((item, idx) => {
              const isActive = location.pathname === item.to;
              return (
                <React.Fragment key={item.to}>
                  <Link
                    to={item.to}
                    aria-current={isActive ? 'page' : undefined}
                    className={`text-[0.875rem] transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent ${
                      isActive
                        ? 'text-accent underline decoration-accent underline-offset-4'
                        : 'text-ink-light/60 hover:text-ink-light'
                    }`}
                  >
                    {item.label}
                  </Link>
                  {idx < FOOTER_LINKS.length - 1 && (
                    <span
                      aria-hidden="true"
                      className="mx-2.5 text-[0.875rem] text-ink-light/40 select-none"
                    >
                      ·
                    </span>
                  )}
                </React.Fragment>
              );
            })}
          </nav>

          {/* Right: Copyright */}
          <div className="text-[0.75rem] text-ink-light/40 font-body">
            All rights reserved © 2026 Goodlad Twinstars.
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
TypeScript
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
TypeScript
// src/pages/Landing.tsx
import React from 'react';
import { TerminalLabel } from '../components/TerminalLabel';
import { Divider } from '../components/Divider';

export const Landing: React.FC = () => {
  return (
    <section className="py-section-mobile md:py-section-desktop wash-atmospheric-135 flex-1">
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel rounded-sharp p-card">
          <TerminalLabel>GRAPH_LAYER: ACTIVE</TerminalLabel>
          <h1 className="mt-4 text-ink">DocugraphAI — Landing</h1>
          <p className="mt-3 text-ink-secondary text-body max-w-2xl">
            Retrievable knowledge. Relational intelligence. Hybrid GraphRAG document intelligence
            for organizations, built by Goodlad Twinstars.
          </p>
          <Divider />
          <p className="font-mono text-terminal text-ink-secondary">
            STATUS: CHROME_INITIALIZED // AWAITING_LANDING_SECTIONS
          </p>
        </div>
      </div>
    </section>
  );
};

export default Landing;
TypeScript
// src/pages/Login.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/GoodladTwinstars_logo.svg';
import { TerminalLabel } from '../components/TerminalLabel';
import { Divider } from '../components/Divider';

export const Login: React.FC = () => {
  return (
    <section className="py-section-mobile md:py-section-desktop wash-atmospheric-225 flex-1 flex items-center">
      <div className="max-w-auth w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Link
            to="/"
            className="inline-flex items-center gap-2 font-mono text-terminal uppercase tracking-[0.02em] text-ink hover:text-ink-secondary border-b border-ink/40 pb-0.5"
          >
            <span aria-hidden="true">←</span>
            <span>Back to home</span>
          </Link>
        </div>

        <div className="glass-panel rounded-card p-card">
          <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
            <img
              src={logo}
              alt="Goodlad Twinstars"
              className="h-[28px] w-auto block"
            />
            <TerminalLabel>ACCESS_MODE: ORG_ONLY</TerminalLabel>
          </div>

          <h1 className="text-ink">Organization Login</h1>
          <p className="mt-3 text-ink-secondary text-body">
            Verified organization email required. Early access for invited pilot organizations.
          </p>
          <Divider />
          <p className="font-mono text-terminal text-ink-secondary">
            AUTH_GATEWAY: STANDBY // PLACEHOLDER_VIEW
          </p>
        </div>
      </div>
    </section>
  );
};

export default Login;
TypeScript
// src/pages/Pricing.tsx
import React from 'react';
import { TerminalLabel } from '../components/TerminalLabel';
import { Divider } from '../components/Divider';

export const Pricing: React.FC = () => {
  return (
    <section className="py-section-mobile md:py-section-desktop bg-secondary flex-1">
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel rounded-sharp p-card">
          <TerminalLabel>PILOT_PROGRAM: EARLY_ACCESS</TerminalLabel>
          <h1 className="mt-4 text-ink">Pricing</h1>
          <p className="mt-3 text-ink-secondary text-body max-w-2xl">
            Organization-level deployment tiers for pilot and enterprise knowledge graphs.
          </p>
          <Divider />
          <p className="font-mono text-terminal text-ink-secondary">
            PRICING_MATRIX: PLACEHOLDER_READY
          </p>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
TypeScript
// src/pages/Terms.tsx
import React from 'react';
import { TerminalLabel } from '../components/TerminalLabel';
import { Divider } from '../components/Divider';

export const Terms: React.FC = () => {
  return (
    <section className="py-section-mobile md:py-section-desktop bg-secondary flex-1">
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel rounded-sharp p-card">
          <TerminalLabel>LEGAL_DOC: TERMS_OF_SERVICE</TerminalLabel>
          <h1 className="mt-4 text-ink">Terms</h1>
          <p className="mt-3 text-ink-secondary text-body max-w-2xl">
            Organizational terms governing pilot access and use of DocugraphAI by Goodlad Twinstars.
          </p>
          <Divider />
          <p className="font-mono text-terminal text-ink-secondary">
            DOCUMENT_STATE: PLACEHOLDER_READY
          </p>
        </div>
      </div>
    </section>
  );
};

export default Terms;
TypeScript
// src/pages/Privacy.tsx
import React from 'react';
import { TerminalLabel } from '../components/TerminalLabel';
import { Divider } from '../components/Divider';

export const Privacy: React.FC = () => {
  return (
    <section className="py-section-mobile md:py-section-desktop bg-secondary flex-1">
      <div className="max-w-landing mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel rounded-sharp p-card">
          <TerminalLabel>DATA_SOVEREIGNTY: YOUR_DATA_STAYS_YOURS</TerminalLabel>
          <h1 className="mt-4 text-ink">Privacy</h1>
          <p className="mt-3 text-ink-secondary text-body max-w-2xl">
            Your data stays yours. Our intelligence works for your profit.
          </p>
          <Divider />
          <p className="font-mono text-terminal text-ink-secondary">
            PRIVACY_SPEC: PLACEHOLDER_READY
          </p>
        </div>
      </div>
    </section>
  );
};

export default Privacy;
TypeScript
// src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Pricing } from './pages/Pricing';
import { Terms } from './pages/Terms';
import { Privacy } from './pages/Privacy';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
TypeScript
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
Markdown
<!-- README.md -->
# DocugraphAI Frontend — Goodlad Twinstars

Marketing and organizational gateway interface for **DocugraphAI**, a Hybrid GraphRAG Document Intelligence Engine built by **Goodlad Twinstars**.

## Prerequisites
- Node.js 18+ and npm 9+
- Ensure the official logo asset is placed at `src/assets/GoodladTwinstars_logo.svg`

## Installation & Local Development

```bash
cd frontend
npm install
npm run dev
Production Build & Verification
Bash
npm run build
npm run preview
Route Map
/ — Landing Page

/login — Organization Login & Pilot Access Request (no top Nav; includes back-to-home link and Footer)

/pricing — Organization & Pilot Tiers

/terms — Terms of Service

/privacy — Privacy & Data Sovereignty Policy


```markdown
<!-- design-system.md -->
# DocugraphAI Retro-Futurism Design System

## 1. Brand Palette (60 / 30 / 10 Rule)
All colors are defined exclusively as CSS custom properties in `src/index.css` under `:root` and mapped in `tailwind.config.ts`. Hardcoded hex values in components are strictly prohibited.

| Role | Token | CSS Variable | Value | Usage |
|---|---|---|---|---|
| **Primary (60%)** | `primary` | `--color-primary` | `#8DB9F0` | Powder Blue — washes, structural highlights, dark-mode mono accents |
| **Secondary (30%)** | `secondary` | `--color-secondary` | `#E9E8F8` | Soft Lavender — primary canvas, card surfaces, logo plate on dark |
| **Accent (10%)** | `accent` | `--color-accent` | `#F5B69E` | Warm Sunset — CTAs, active route indicators, terminal tags |
| **Primary Ink** | `ink` | `--color-ink` | `#101828` | Charcoal Blue — primary typography, borders, dark footer surface |
| **Secondary Ink** | `ink-secondary` | `--color-ink-secondary` | `#2C3E50` | Secondary body copy and muted structural labels |
| **Light Ink** | `ink-light` | `--color-ink-light` | `#E9E8F8` | Lavender white — headings and copy on `--color-ink` surfaces |

### Contrast Guardrails
- Never render white text directly on `--color-primary` (`#8DB9F0`) or `--color-accent` (`#F5B69E`). Always pair those surfaces with `--color-ink` (`#101828`).
- On `--color-ink` (`#101828`) surfaces, use `--color-ink-light` (`#E9E8F8`), `--color-primary` (`#8DB9F0`), or `--color-accent` (`#F5B69E`).

## 2. Typography & Modular Scale (1.25 Ratio)
- **Headings (`--font-heading`)**: `'Space Grotesk', sans-serif` — tight tracking (`-0.02em` to `-0.04em`).
- **Body (`--font-body`)**: `'Inter', sans-serif` — tracking `0`.
- **Technical / Monospace (`--font-mono`)**: `'JetBrains Mono', monospace` — tracking `0.02em`.
- **Scale**:
  - `H1`: `3.5rem` desktop / `2.5rem` mobile
  - `H2`: `2.5rem` desktop / `2.0rem` mobile
  - `H3`: `1.75rem` desktop / `1.5rem` mobile
  - `Body`: `1rem`
  - `Small`: `0.875rem`
  - `Terminal`: `0.75rem`

## 3. Geometry, Spacing & Layout
- **Grid**: 12-column CSS Grid (`.grid-12`), `24px` column gutter, `16px` card gap.
- **Max Widths**: `1200px` (`max-w-landing`) for marketing/legal pages; `960px` (`max-w-auth`) for `/login`.
- **Section Padding**: `80px` vertical desktop (`py-section-desktop`), `48px` mobile (`py-section-mobile`).
- **Card Padding**: `32px` (`p-card`).
- **Border Radii**:
  - Primary containers: `0px` (`--radius-sharp` / `rounded-sharp`)
  - Cards: `8px` (`--radius-card` / `rounded-card`)
  - Buttons & tags: `4px` (`--radius-button` / `rounded-button`)
  - Never use `9999px` pill shapes or drop shadows on cards.

## 4. Atmospheric Surfaces & Retro-Futuristic Accents
- **Directional Washes**: `.wash-atmospheric-135`, `.wash-atmospheric-225`, `.wash-atmospheric-180` — slow `8s–9s` ambient shifts; horizontal `90deg` gradients are forbidden.
- **Analog Grain**: `.grain-surface::after` applies a fixed `2.5%` opacity SVG fractal-noise overlay across the viewport.
- **Glassmorphism**: `.glass-panel` (`backdrop-filter: blur(12px)`, `rgba(233, 232, 248, 0.6)`, `1px solid rgba(141, 185, 240, 0.3)`), reserved strictly for sticky navigation and floating cards.
- **Scan Lines**: `.scanlines-dark` and `.scanlines-light` render `1px` horizontal lines every `24px` at `0.03` opacity.
- **Motion Safety**: All keyframe animations and transitions are disabled under `@media (prefers-reduced-motion: reduce)`.

## 5. Frozen Shared Components
- **`<Nav />`**: Sticky header with transparent-to-glass scroll transition, official Goodlad Twinstars SVG logo (`36px` desktop, `30px` mobile), links (`/#product`, `/#enterprise`, `/pricing`, `Docs` coming-soon), and `Request org access` CTA (`/login#request-access`). Frozen after Prompt 1.
- **`<Footer />`**: Dark ink (`--color-ink`) surface with scanlines, `28px` logo inside a `--color-secondary` plate (`8px` padding, `4px` radius), monospace engine descriptor, 5 route links with `aria-current="page"`, copyright notice, and `1px` Peach bottom border at `0.3` opacity. Frozen after Prompt 1.
- **`<Button />`**: `primary` (Peach fill, Ink text, `4px` radius, hover glow) and `secondary` (transparent fill, `1px` Ink border, Ink text, `4px` radius).
- **`<TerminalLabel />`**: Monospace `0.75rem` tag in `--color-accent` on `--color-ink` pill container with square status indicator.
- **`<Divider />`**: Architectural rule with center geometric diamond-crosshair SVG node.
Browser Verification Checklist
Confirm the sticky <Nav /> renders the Goodlad Twinstars logo at 36px height on desktop (30px on mobile), transitions from transparent to blur(12px) glassmorphism on scroll, displays "Coming soon" on Docs hover, and highlights active routes with aria-current="page" and a Warm Sunset (--color-accent) underline.

Verify all 5 routes (/, /login, /pricing, /terms, /privacy) navigate cleanly, with /login omitting the top <Nav />, rendering the "Back to home" link, and displaying the 28px logo at the top of the 960px-max-width auth card.

Inspect <Footer /> across all pages to confirm the dark ink (--color-ink) background with subtle scan lines, the 28px logo inside its Soft Lavender (--color-secondary) plate (8px padding, 4px radius, no shadow), center route links separated by ·, and the 1px Warm Sunset bottom border at 30% opacity.

Check <Button />, <TerminalLabel />, and <Divider /> for sharp/4px/8px architectural geometry (zero pill shapes or card drop shadows), WCAG AA/AAA ink contrast on Powder Blue and Warm Sunset surfaces, and the subtle SVG grain overlay.

Toggle prefers-reduced-motion: reduce in DevTools Rendering settings and verify that the 135deg/225deg atmospheric gradient washes and UI transitions immediately stop animating.

Assumption: Added src/vite-env.d.ts and src/styles/tokens.ts alongside src/index.css so TypeScript cleanly resolves the .svg logo module import and the src/styles/ token directory from your initial architecture spec is present.