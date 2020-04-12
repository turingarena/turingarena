import { gql } from '@apollo/client';
import { contestProblemAssignmentUserTacklingSubmissionListModalFragment } from './contest-problem-assignment-user-tackling-submission-list-modal';
import { contestProblemAssignmentUserTacklingSubmitModalFragment } from './contest-problem-assignment-user-tackling-submit-modal';
import { submissionModalFragment } from './submission-modal';

export const contestProblemAssignmentUserTacklingAsideFragment = gql`
  fragment ContestProblemAssignmentUserTacklingAside on ContestProblemAssignmentUserTackling {
    canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }

      ...SubmissionModal
    }

    ...ContestProblemAssignmentUserTacklingSubmitModal
    ...ContestProblemAssignmentUserTacklingSubmissionListModal
  }

  ${submissionModalFragment}
  ${contestProblemAssignmentUserTacklingSubmitModalFragment}
  ${contestProblemAssignmentUserTacklingSubmissionListModalFragment}
`;
