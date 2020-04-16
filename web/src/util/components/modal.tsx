import { css, cx } from 'emotion';
import React, { ReactNode, useEffect, useState } from 'react';
import { useAsync } from '../async-hook';
import { animationFrame, delay } from '../delay';

interface Props {
  onClose: () => void;
  show?: boolean;
  children: ReactNode;
}

export const modalHeaderCss = 'modal-header';
export const modalBodyCss = 'modal-body';
export const modalFooterCss = 'modal-footer';

export function Modal({ onClose, show = true, children }: Props) {
  const [show1, setShow1] = useState(false);
  const [show2, setShow2] = useState(false);

  const [animate, { loading: animating }] = useAsync(async () => {
    if (show) {
      setShow1(show);
      await animationFrame();
      setShow2(show);
    } else {
      setShow2(show);
      await delay(300);
      await animationFrame();
      setShow1(show);
    }
  });

  useEffect(() => {
    if (!animating) {
      animate();
    }
  }, [show, animate, animating]);

  if (!show1) return <></>;

  return (
    <>
      <div
        className={cx(
          'modal',
          'fade',
          ...(show1
            ? [
                css`
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  pointer-events: none;
                `,
              ]
            : []),
          ...(show2 ? ['show'] : []),
        )}
      >
        <div
          className={cx(
            'modal-dialog',
            css`
              width: auto;
              max-width: none;
            `,
          )}
        >
          <div className={cx('modal-content')}>{children}</div>
        </div>
      </div>
      <div
        className={cx(
          'modal-backdrop',
          'fade',
          ...(show2 ? ['show'] : []),
          // css`
          //   z-index: 1051;
          // `,
        )}
        onClick={onClose}
      ></div>
    </>
  );
}
