import { gql } from '@apollo/client';
import { css, cx } from 'emotion';
import React from 'react';
import { ContestProblemAssignmentUserTacklingSubmissionListModalFragment } from '../generated/graphql-types';
import { buttonCss, buttonPrimaryCss } from '../util/components/button';
import { gridCss } from '../util/components/grid';
import { modalFooterCss, modalHeaderCss } from '../util/components/modal';
import { FragmentProps } from '../util/fragment-props';
import {
  ContestProblemAssignmentUserTacklingSubmissionList,
  contestProblemAssignmentUserTacklingSubmissionListFragment,
} from './contest-problem-assignment-user-tackling-submission-list';
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

export function ContestProblemAssignmentUserTacklingSubmissionListModal({
  data,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmissionListModalFragment>) {
  return (
    <>
      <div className={modalHeaderCss}>
        <h4>
          Submissions for: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
        </h4>
      </div>
      <div
        className={cx(
          gridCss,
          css`
            padding: 0;
            max-height: calc(100vh - 260px);
            overflow-y: auto;
          `,
        )}
      >
        <ContestProblemAssignmentUserTacklingSubmissionList data={data} />
      </div>
      <div className={modalFooterCss}>
        <button onClick={() => console.error('TODO')} className={cx(buttonCss, buttonPrimaryCss)}>
          Close
        </button>
      </div>
    </>
  );
}
