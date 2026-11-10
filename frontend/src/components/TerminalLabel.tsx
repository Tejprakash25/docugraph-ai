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