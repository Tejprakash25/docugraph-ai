// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
        ink: 'var(--color-ink)',
        'ink-secondary': 'var(--color-ink-secondary)',
        'ink-light': 'var(--color-ink-light)',
      },
      fontFamily: {
        heading: ['var(--font-heading)'],
        body: ['var(--font-body)'],
        mono: ['var(--font-mono)'],
      },
      fontSize: {
        h1: ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.03em', fontWeight: '700' }],
        h2: ['2.5rem', { lineHeight: '1.15', letterSpacing: '-0.025em', fontWeight: '600' }],
        h3: ['1.75rem', { lineHeight: '1.25', letterSpacing: '-0.02em', fontWeight: '600' }],
        body: ['1rem', { lineHeight: '1.6', letterSpacing: '0' }],
        small: ['0.875rem', { lineHeight: '1.5', letterSpacing: '0' }],
        terminal: ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.02em' }],
      },
      borderRadius: {
        sharp: 'var(--radius-sharp)',
        card: 'var(--radius-card)',
        button: 'var(--radius-button)',
      },
      boxShadow: {
        glass: 'var(--shadow-glass)',
        'accent-glow': 'var(--shadow-accent-glow)',
      },
      maxWidth: {
        landing: '1200px',
        auth: '960px',
      },
      spacing: {
        'section-desktop': '80px',
        'section-mobile': '48px',
        card: '32px',
        gutter: '24px',
        'card-gap': '16px',
      },
    },
  },
  plugins: [],
};

export default config;