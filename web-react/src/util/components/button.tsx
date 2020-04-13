import { css } from 'emotion';
import React from 'react';

interface ButtonProps {
  title: string;
  disabled?: boolean;
  onPress: () => void;
}

export function Button({ onPress, title, disabled }: ButtonProps) {
  return (
    <button onClick={onPress} disabled={disabled} className={css``}>
      {title}
    </button>
  );
}
