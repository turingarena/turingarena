import gql from 'graphql-tag';

import { AwardFragment } from './__generated__/AwardFragment';
import { ProblemViewFragment } from './__generated__/ProblemViewFragment';
import { SubmissionFragment } from './__generated__/SubmissionFragment';
import { awardOutcomeFragment } from './awards';

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
      awards {
        ...AwardOutcomeFragment
      }
      totalScore
    }
  }
  ${awardOutcomeFragment}
`;

export const getSubmissionState = (problem: ProblemViewFragment, submission: SubmissionFragment) => ({
  score: submission.evaluation.totalScore,
  range: problem.totalScoreRange,
  award: ({ name, content }: AwardFragment) => ({
    score: 0,
    badge: false,
    ...submission.evaluation.awards.filter((s) => s.awardName === name).map((s) => s.value).find(() => true),
    ...content.__typename === 'ScoreAwardContent' ? {
      range: content.range,
    } : {},
  }),
});
