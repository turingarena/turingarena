import gql from 'graphql-tag';

import { fileFragment } from './file';
import { problemViewFragment } from './problem';
import { scoreRangeFragment } from './score';
import { textFragment } from './text';

export const contestMaterialFragment = gql`
  fragment ContestMaterialFragment on ContestMaterial {
    title {
      ...TextFragment
    }
    description {
      ...FileFragment
    }
    attachments {
      title {
        ...TextFragment
      }
      file {
        ...FileFragment
      }
    }
    resources {
      title {
        ...TextFragment
      }
      file {
        ...FileFragment
      }
    }
    startTime
    endTime
  }

  ${textFragment}
  ${fileFragment}
`;

export const contestViewFragment = gql`
  fragment ContestViewFragment on ContestView {
    user {
      ...UserFragment
    }
    material {
      ...ContestMaterialFragment
    }
    problems {
      ...ProblemViewFragment
    }
    totalScoreRange {
      ...ScoreRangeFragment
    }
    totalScore
  }

  fragment UserFragment on User {
    id
    displayName
  }

  ${contestMaterialFragment}
  ${problemViewFragment}
  ${scoreRangeFragment}
`;
