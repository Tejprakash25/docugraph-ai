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
