import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React from 'react';
import { Link } from 'react-router-dom';
import { TopBarFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { textFragment } from './text';

export function TopBar({ data }: FragmentProps<TopBarFragment>) {
  return (
    <nav className="top-bar">
      <Link to="/">
        <h1 className="top-bar-title">
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
