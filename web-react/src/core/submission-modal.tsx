import { gql } from '@apollo/client';
import { columnFragment, recordFragment } from './field-table';
import { textFragment } from './text';

export const submissionModalFragment = gql`
  fragment SubmissionModal on Submission {
    id
    # TODO: files
    createdAt {
      local
    }
    officialEvaluation {
      status
    }
    problem {
      id
      title {
        ...Text
      }
    }
    feedbackTable {
      columns {
        ...Column
      }
      rows {
        ...Record
      }
    }
  }

  ${textFragment}
  ${recordFragment}
  ${columnFragment}
`;
