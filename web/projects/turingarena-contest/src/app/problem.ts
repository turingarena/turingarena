import gql from 'graphql-tag';

export const problemFragment = gql`
  fragment ProblemStateFragment on Problem {
    scores {
      awardName
      score
      submissionId
    }
    badges {
      awardName
      badge
      submissionId
    }
  }
`;
