import { css } from 'emotion';
import React from 'react';
import { Theme } from '../theme';

interface ButtonProps {
  disabled?: boolean;
  className?: string;
  primary?: boolean;
  type?: 'button' | 'submit' | 'reset';
  children: React.ReactNode;
  onPress: () => void;
}

export function Button({ onPress, children, disabled, className = '', primary, type }: ButtonProps) {
  const style = css`
    border-radius: 4px;
    padding: 5px 10px;
    text-decoration: none;
    display: inline-block;
    font-size: 14px;
    transition: 0.3s;
    ${primary === true ? `background-color: ${Theme.colors.primary};` : ''}
    color: ${primary === true ? '#f7f7f7' : '#292b2c'};
    border-width: 0.5px;
    border-color: ${primary === true ? '#f7f7f7' : '#292b2c'};

    &:focus {
      outline: none;
      border-color: #292b2c;
    }

    &:hover {
      background-color: ${primary === true ? '#004e91' : '#e7e7e7'};
    }
  `;

  return (
    <button onClick={onPress} disabled={disabled} type={type} className={`${style} ${className}`}>
      {children}
    </button>
  );
}
