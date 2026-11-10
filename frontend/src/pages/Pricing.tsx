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
