import { gql } from '@apollo/client';
import React from 'react';
import { MainViewFragment } from '../generated/graphql-types';
import { contestViewFragment } from './contest-view';
import { topBarFragment } from './top-bar';

export function MainView({ data }: { data: MainViewFragment }) {
  return <div>{JSON.stringify(data)}</div>;
}

export const mainViewFragment = gql`
  fragment MainView on MainView {
    ...TopBar
    contestView {
      ...ContestView
    }
  }

  ${topBarFragment}
  ${contestViewFragment}
`;
