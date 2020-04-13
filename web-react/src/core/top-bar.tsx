import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React from 'react';
import { Link } from 'react-router-dom';
import { TopBarFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { textFragment } from './text';

export function TopBar({ data }: FragmentProps<TopBarFragment>) {
  return (
    <nav
      className={css`
        display: flex;
        background-color: #0275d8;
        align-items: center;
        padding: 8px 16px;
        color: #fff;
      `}
    >
      <Link to="/">
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
    </nav>
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
