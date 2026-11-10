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