import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import { Modal } from 'react-bootstrap';
import { defineMessage, FormattedMessage, MessageDescriptor, useIntl } from 'react-intl';
import { Link } from 'react-router-dom';
import { TopBarFragment } from '../generated/graphql-types';
import { useAuth } from '../util/auth';
import { buttonCss, buttonLightCss, buttonSmallCss } from '../util/components/button';
import { FragmentProps } from '../util/fragment-props';
import { SupportedLanguage, supportedLanguageList, useLanguageSettings } from '../util/intl';
import { Theme } from '../util/theme';
import { textFragment } from './data/text';
import { LoginModal } from './login-modal';
import { MessagesModal } from './messages-modal';

const languageLabels: Record<SupportedLanguage, MessageDescriptor> = {
  en: defineMessage({ id: 'language-en', defaultMessage: `English` }),
  it: defineMessage({ id: 'language-it', defaultMessage: `Italian` }),
};

export function TopBar({ data }: FragmentProps<TopBarFragment>) {
  const [showLogInModal, setShowLogInModal] = useState(false);
  const [showMessagesModal, setShowMessagesModal] = useState(false);
  const auth = useAuth();
  const languageSettings = useLanguageSettings();

  const intl = useIntl();
  const languageList = supportedLanguageList.map(name => ({ name, label: intl.formatMessage(languageLabels[name]) }));
  languageList.sort((a, b) => (a.label < b.label ? -1 : +1));

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
            <Link to="/dashboard">
              <button
                className={cx(
                  buttonCss,
                  buttonLightCss,
                  buttonSmallCss,
                  css`
                    margin-right: 5px;
                  `,
                )}
              >
                <FontAwesomeIcon icon="tachometer-alt" /> Dashboard
              </button>
            </Link>
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
              <FontAwesomeIcon icon="envelope" />{' '}
              <FormattedMessage id="messages-button-label" defaultMessage="Messages" />
            </button>
            <button
              className={cx(buttonCss, buttonLightCss, buttonSmallCss)}
              onClick={() => {
                auth.clearAuth();
              }}
            >
              <FontAwesomeIcon icon="sign-out-alt" />{' '}
              <FormattedMessage id="log-out-button-label" defaultMessage="Log out" />
            </button>
          </>
        )}
        {data.user === null && (
          <button className={cx(buttonCss, buttonLightCss, buttonSmallCss)} onClick={() => setShowLogInModal(true)}>
            <FontAwesomeIcon icon="sign-in-alt" /> <FormattedMessage id="log-in-button-label" defaultMessage="Log in" />
          </button>
        )}
        <select
          value={languageSettings.overrideLanguage ?? ''}
          className={cx(
            'custom-select',
            'custom-select-sm',
            css`
              margin-left: 5px;
              color: #212529;
              width: auto;
            `,
          )}
          onChange={e => languageSettings.setOverrideLanguage((e.target.value || null) as SupportedLanguage | null)}
        >
          <option value="">
            {intl.formatMessage(
              defineMessage({
                id: 'language-auto-option',
                defaultMessage: `Auto: {value}`,
              }),
              { value: intl.formatMessage(languageLabels[languageSettings.autoLanguage]) },
            )}
          </option>
          {languageList.map(({ name, label }) => (
            <option value={name}>{label}</option>
          ))}
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
