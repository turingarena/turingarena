import { gql } from '@apollo/client';
import { contestProblemAssignmentUserTacklingSubmissionListFragment } from './contest-problem-assignment-user-tackling-submission-list';
import { textFragment } from './text';

export const contestProblemAssignmentUserTacklingSubmissionListModalFragment = gql`
  fragment ContestProblemAssignmentUserTacklingSubmissionListModal on ContestProblemAssignmentUserTackling {
    assignmentView {
      assignment {
        problem {
          title {
            ...Text
          }
        }
      }
    }

    ...ContestProblemAssignmentUserTacklingSubmissionList
  }

  ${textFragment}
  ${contestProblemAssignmentUserTacklingSubmissionListFragment}
`;
