import { gql } from '@apollo/client';
import { contestViewFragment } from './contest-view';
import { topBarFragment } from './top-bar';

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
