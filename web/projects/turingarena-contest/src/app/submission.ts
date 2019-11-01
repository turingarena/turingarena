import gql from 'graphql-tag';
import { ProblemMaterialFragment } from './__generated__/ProblemMaterialFragment';
import { SubmissionFragment } from './__generated__/SubmissionFragment';

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

export const getSubmissionState = (problem: ProblemMaterialFragment, submission: SubmissionFragment) => ({
  score: problem.material.awards
    .map((award) => submission.scores.find((s) => s.awardName === award.name))
    .map((state) => state !== undefined ? state.score as number : 0)
    .reduce((a, b) => a + b, 0),
  award: ({ name }: { name: string }) => ({
    score: 0,
    badge: false,
    ...submission.scores.find((s) => s.awardName === name),
    ...submission.badges.find((s) => s.awardName === name),
  }),
});
