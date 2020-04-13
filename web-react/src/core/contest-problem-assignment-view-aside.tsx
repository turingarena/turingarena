import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { ContestProblemAssignmentViewAsideFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import {
  ContestProblemAssignmentUserTacklingAside,
  contestProblemAssignmentUserTacklingAsideFragment,
} from './contest-problem-assignment-user-tackling-aside';
import { gradeFieldFragment, scoreFieldFragment } from './fields/grade-field';
import { mediaDownloadFragment } from './media-download';
import { mediaInlineFragment } from './media-inline';
import { textFragment } from './text';

export const contestProblemAssignmentViewAsideFragment = gql`
  fragment ContestProblemAssignmentViewAside on ContestProblemAssignmentView {
    assignment {
      id
      problem {
        id
        name
        title {
          ...Text
        }
        statement {
          ...MediaInline
          ...MediaDownload
        }
        attachments {
          title {
            ...Text
          }
          media {
            ...MediaDownload
          }
        }
      }
    }

    totalScoreField {
      ...ScoreField
    }

    awardAssignmentViews {
      assignment {
        id
        award {
          id
          name
          title {
            ...Text
          }
        }
      }

      gradeField {
        ...GradeField
      }
    }

    tackling {
      ...ContestProblemAssignmentUserTacklingAside
    }
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${mediaDownloadFragment}
  ${scoreFieldFragment}
  ${gradeFieldFragment}
  ${contestProblemAssignmentUserTacklingAsideFragment}
`;

export function ContestProblemAssignmentViewAside({ data }: FragmentProps<ContestProblemAssignmentViewAsideFragment>) {
  return (
    <div
      className={css`
        flex: 0 0 auto;
        width: 15em;
        background-color: #f8f9fa;
      `}
    >
      {data.tackling !== null && <ContestProblemAssignmentUserTacklingAside data={data.tackling} />}
    </div>
  );
}
