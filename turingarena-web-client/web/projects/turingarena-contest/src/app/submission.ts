import gql from 'graphql-tag';

import { AwardFragment } from './__generated__/AwardFragment';
import { MaterialFragment } from './__generated__/MaterialFragment';
import { SubmissionFragment } from './__generated__/SubmissionFragment';
import { awardOutcomeFragment } from './awards';
import { getProblemScoreRange } from './material';

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
    status
    awards {
      ...AwardOutcomeFragment
    }
  }
  ${awardOutcomeFragment}
`;

export const getSubmissionState = (material: MaterialFragment, submission: SubmissionFragment) => ({
  score: material.awards
    .map((award) => submission.awards.find((s) => s.awardName === award.name))
    .map((state) => state !== undefined && state.value.__typename === 'ScoreAwardValue' ? state.value.score : 0)
    .reduce((a, b) => a + b, 0),
  range: getProblemScoreRange(material),
  award: ({ name, content }: AwardFragment) => ({
    score: 0,
    badge: false,
    ...submission.awards.filter((s) => s.awardName === name).map((s) => s.value).find(() => true),
    ...content.__typename === 'ScoreAwardContent' ? {
      range: content.range,
    } : {},
  }),
});
