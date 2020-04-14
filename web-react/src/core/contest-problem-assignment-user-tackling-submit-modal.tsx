import { gql } from '@apollo/client';
import { css, cx } from 'emotion';
import React from 'react';
import { ContestProblemAssignmentUserTacklingSubmitModalFragment } from '../generated/graphql-types';
import { modalBodyCss, modalHeaderCss } from '../util/components/modal';
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
  return (
    <form>
      <div className={modalHeaderCss}>
        <h4>
          Solution of: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
        </h4>
      </div>
      <div
        className={cx(
          modalBodyCss,
          css`
            max-height: calc(100vh - 260px);
            overflow-y: auto;
          `,
        )}
      >
        {data.assignmentView.assignment.problem.submissionFields.map(f => {
          const fileFieldId = `${f.name}.file`;

          return (
            <React.Fragment key={f.name}>
              <label
                className={css`
                  display: block;
                `}
                htmlFor={fileFieldId}
              >
                {f.title.variant}
              </label>
              <input
                className={css`
                  display: none;
                `}
                id={fileFieldId}
                name={fileFieldId}
                type="file"
                onChange={() => {
                  // TODO
                }}
              />
            </React.Fragment>
          );
        })}
      </div>
    </form>
  );
}
