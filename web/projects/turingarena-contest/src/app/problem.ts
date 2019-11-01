import gql from 'graphql-tag';

export const problemFragment = gql`
  fragment ProblemTacklingFragment on ProblemTackling {
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
    canSubmit
  }
`;
