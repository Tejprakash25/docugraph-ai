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