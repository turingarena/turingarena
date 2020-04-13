import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { TopBarFragment } from '../generated/graphql-types';
import { buttonCss, buttonLightCss, buttonPrimaryCss } from '../util/components/button';
import { Modal } from '../util/components/modal';
import { FragmentProps } from '../util/fragment-props';
import { Theme } from '../util/theme';
import { LoginModal } from './login-modal';
import { textFragment } from './text';

export function TopBar({ data }: FragmentProps<TopBarFragment>) {
  const [showLogInModal, setShowLogInModal] = useState(false);

  return (
    <>
      <Modal show={showLogInModal} onClose={() => setShowLogInModal(false)}>
        <LoginModal onClose={() => setShowLogInModal(false)} />
      </Modal>
      <nav
        className={css`
          display: flex;
          background-color: ${Theme.colors.primary};
          align-items: center;
          padding: 8px 16px;
          color: #fff;
        `}
      >
        <Link
          to="/"
          className={css`
            display: block;

            margin: -8px 0;
            padding: 8px 0;

            color: white;
            text-decoration: none;
            background-color: transparent;

            &:hover {
              text-decoration: none;
              color: white;
            }

            margin-right: auto;
          `}
        >
          <h1
            className={css`
              display: block;
              margin: 0;
              font-size: 1.25rem;
              font-weight: 400;
              line-height: inherit;
              white-space: nowrap;
            `}
          >
            <FontAwesomeIcon icon="home" /> {data.title.variant}
          </h1>
        </Link>
        {data.user !== null && (
          // TODO: admin button
          <button
            className={cx(buttonCss, buttonPrimaryCss)}
            onClick={() => {
              console.warn('TODO');
            }}
          >
            <FontAwesomeIcon icon="sign-out-alt" /> Logout
          </button>
        )}
        {/* {data.user === null && ( */}
        <button className={cx(buttonCss, buttonLightCss)} onClick={() => setShowLogInModal(true)}>
          <FontAwesomeIcon icon="sign-in-alt" /> Login
        </button>
        {/* )} */}
      </nav>
    </>
  );
}

export const topBarFragment = gql`
  fragment TopBar on MainView {
    title {
      ...Text
    }
    user {
      id
      name
    }
  }

  ${textFragment}
`;
