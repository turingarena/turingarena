import { css } from 'emotion';
import React from 'react';

interface Props {
  onClose: () => void;
  show: boolean;
  children: React.ReactElement;
}

export function Modal({
  onClose,
  show = true,
  children
}: Props) {
  return show && (
    <div>
      <div
        onClick={onClose}
        className={css`
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 100;
          background-color: rgba(0, 0, 0, 0.3);
        `}
      />

      <div
        className={css`
          position: fixed;
          top: 100px;
          left: 400px;
          right: 400px;
          bottom: 100px;
          z-index: 101;
          background-color: white;
        `}
      >
        {children}
      </div>
    </div>
  );
}
