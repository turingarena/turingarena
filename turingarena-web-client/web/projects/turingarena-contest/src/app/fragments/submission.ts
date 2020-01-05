import gql from 'graphql-tag';

import { awardAchievementFragment, scoreAwardDomainFragment, scoreAwardGradeFragment } from './awards';

export const submissionFragment = gql`
  fragment SubmissionFragment on Submission {
    id
    createdAt
    files {
      fieldId
      typeId
      name
      content {
        base64
      }
    }
    evaluation {
      status
      achievements {
        ...AwardAchievementFragment
      }
      totalScore {
        ...ScoreAwardGradeFragment
      }
    }
  }

  ${awardAchievementFragment}
  ${scoreAwardGradeFragment}
`;
