import gql from 'graphql-tag';

import { AwardFragment } from './__generated__/AwardFragment';
import { MaterialFragment } from './__generated__/MaterialFragment';
import { SubmissionFragment } from './__generated__/SubmissionFragment';
import { getProblemScoreRange } from './material';

export const submissionFragment = gql`
  fragment SubmissionFragment on Submission {
    id
    createdAt
    files {
      fieldId
      typeId
      name
      contentBase64
    }
    status
    scores {
      awardName
      score
    }
    badges {
      awardName
      badge
    }
  }
`;

export const getSubmissionState = (material: MaterialFragment, submission: SubmissionFragment) => ({
  score: material.awards
    .map((award) => submission.scores.find((s) => s.awardName === award.name))
    .map((state) => state !== undefined ? state.score as number : 0)
    .reduce((a, b) => a + b, 0),
  range: getProblemScoreRange(material),
  award: ({ name, content }: AwardFragment) => ({
    score: 0,
    badge: false,
    ...submission.scores.find((s) => s.awardName === name),
    ...submission.badges.find((s) => s.awardName === name),
    ...content.__typename === 'ScoreAwardContent' ? {
      range: content.range,
    } : {},
  }),
});
