import { gql } from '@apollo/client';
import React from 'react';
import { ContestProblemAssignmentUserTacklingSubmitModalFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { textFragment } from './text';

export const contestProblemAssignmentUserTacklingSubmitModalFragment = gql`
  fragment ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType on SubmissionFileType {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmitModalSubmissionField on SubmissionField {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileTypeRule on SubmissionFileTypeRule {
    fields {
      name
    }
    extensions
    defaultType {
      ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType
    }
    recommendedTypes {
      ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType
    }
    otherTypes {
      ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmitModal on ContestProblemAssignmentUserTackling {
    assignmentView {
      assignment {
        contest {
          name
        }
        problem {
          name
          title {
            ...Text
          }
          submissionFields {
            ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionField
          }
          submissionFileTypeRules {
            ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileTypeRule
          }
        }
      }
    }

    user {
      username
    }
  }

  ${textFragment}
`;

export function ContestProblemAssignmentUserTacklingSubmitModal({
  data,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmitModalFragment>) {
  return <>Yeah!</>;
}
