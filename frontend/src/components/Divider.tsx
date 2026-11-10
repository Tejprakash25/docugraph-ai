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