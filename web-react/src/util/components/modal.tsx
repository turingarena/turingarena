import { css } from 'emotion';
import React from 'react';

interface Props {
  onClose: () => void;
  show: boolean;
  children: React.ReactElement;
}

export function Modal({ onClose, show = true, children }: Props) {
  return show ? (
    <>
      <div
        onClick={onClose}
        className={css`
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 100;
          background-color: rgba(0, 0, 0, 0.5);
        `}
      />

      <div
        className={css`
          align-self: center;
          position: fixed;
          border-radius: 5px;
          top: 70px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 101;
          background-color: white;
          border: 1px solid rgba(0, 0, 0, 0.2);
          padding: 1rem;
        `}
      >
        {children}
      </div>
    </>
  ) : (
    <></>
  );
}
