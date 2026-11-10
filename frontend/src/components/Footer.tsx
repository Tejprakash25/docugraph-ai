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