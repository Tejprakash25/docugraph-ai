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