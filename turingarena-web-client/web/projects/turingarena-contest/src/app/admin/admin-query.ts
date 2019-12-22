import gql from 'graphql-tag';

import { awardOutcomeFragment } from '../awards';
import { problemMaterialFragment } from '../material';
import { textFragment } from '../text';

export const adminQuery = gql`
  fragment AdminProblemFragment on Problem {
    name
    material {
      ...MaterialFragment
    }
  }

  fragment AdminUserFragment on User {
    id
    displayName
  }

  fragment AdminAwardFragment on AwardOutcome {
    submission {
      problemName
      userId
    }
    ...AwardOutcomeFragment
  }

  fragment AdminSubmissionFragment on Submission {
    id
    problemName
    userId
  }

  query AdminQuery {
    serverTime
    contestView {
      title { ...TextFragment }
      startTime
      endTime
    }
    problems {
      ...AdminProblemFragment
    }
    users {
      ...AdminUserFragment
    }
    awards {
      ...AdminAwardFragment
    }
    submissions {
      ...AdminSubmissionFragment
    }
  }
  ${awardOutcomeFragment}
  ${problemMaterialFragment}
  ${textFragment}
`;
