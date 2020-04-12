import { gql } from '@apollo/client';

export const contestViewClockFragment = gql`
  fragment ContestViewClock on ContestView {
    contest {
      start
      end
      status
    }
  }
`;
