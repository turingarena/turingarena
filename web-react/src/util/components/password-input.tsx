import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React, { useState } from 'react';

interface PasswordInputProps {
  password: string;
  onChange: (password: string) => void;
}

export function PasswordInput({ password, onChange }: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div
      className={css`
        position: relative;
        display: inline-block;
      `}
    >
      <input
        type={showPassword ? 'text' : 'password'}
        value={password}
        onChange={e => onChange(e.target.value)}
        className={css`
          width: 100%;
          border-width: 0 0 2px;
          font-size: 16pt;

          &:focus {
            outline: none;
          }
        `}
      />
      <a
        onClick={() => setShowPassword(!showPassword)}
        className={css`
          position: absolute;
          right: 5px;
          bottom: 5px;
        `}
      >
        <FontAwesomeIcon icon="eye" color={!showPassword ? '#000000' : '#707070'} />
      </a>
    </div>
  );
}
