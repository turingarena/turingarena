import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import { Modal } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { TopBarFragment } from '../generated/graphql-types';
import { useAuth } from '../util/auth';
import { buttonCss, buttonLightCss, buttonSmallCss } from '../util/components/button';
import { FragmentProps } from '../util/fragment-props';
import { Theme } from '../util/theme';
import { LoginModal } from './login-modal';
import { MessagesModal } from './messages-modal';
import { textFragment } from './text';

export function TopBar({ data }: FragmentProps<TopBarFragment>) {
  const [showLogInModal, setShowLogInModal] = useState(false);
  const [showMessagesModal, setShowMessagesModal] = useState(false);
  const auth = useAuth();
  const { t, i18n } = useTranslation();

  return (
    <>
      <Modal show={showLogInModal} onHide={() => setShowLogInModal(false)} autoFocus={false} animation={false}>
        <LoginModal onClose={() => setShowLogInModal(false)} />
      </Modal>
      <Modal show={showMessagesModal} onHide={() => setShowMessagesModal(false)} animation={false} size="lg">
        <MessagesModal onClose={() => setShowMessagesModal(false)} />
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
          <>
            <span
              className={css`
                margin-right: 10px;
              `}
            >
              {data.user.name}
            </span>
            <button
              className={cx(
                buttonCss,
                buttonLightCss,
                buttonSmallCss,
                css`
                  margin-right: 5px;
                `,
              )}
              onClick={() => setShowMessagesModal(true)}
            >
              <FontAwesomeIcon icon="envelope" /> {t('messages')}
            </button>
            <button
              className={cx(buttonCss, buttonLightCss, buttonSmallCss)}
              onClick={() => {
                auth.clearAuth();
              }}
            >
              <FontAwesomeIcon icon="sign-out-alt" /> {t('logOut')}
            </button>
          </>
        )}
        {data.user === null && (
          <button className={cx(buttonCss, buttonLightCss, buttonSmallCss)} onClick={() => setShowLogInModal(true)}>
            <FontAwesomeIcon icon="sign-in-alt" /> {t('logIn')}
          </button>
        )}
        <select
          value={i18n.language.substr(0, 2)}
          className={cx(
            'custom-select',
            'custom-select-sm',
            css`
              margin-left: 5px;
              color: #212529;
              width: auto;
            `,
          )}
          onChange={e => i18n.changeLanguage(e.target.value)}
        >
          <option value="it">Italiano</option>
          <option value="en">English</option>
        </select>
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
