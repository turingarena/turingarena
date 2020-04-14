import { gql } from '@apollo/client';
import { css, cx } from 'emotion';
import React from 'react';
import { ContestProblemAssignmentViewAsideFragment } from '../generated/graphql-types';
import { badgeCss, getBadgeCssByValence } from '../util/components/badge';
import { FragmentProps } from '../util/fragment-props';
import {
  ContestProblemAssignmentUserTacklingAside,
  contestProblemAssignmentUserTacklingAsideFragment,
} from './contest-problem-assignment-user-tackling-aside';
import { GradeField, gradeFieldFragment, scoreFieldFragment } from './fields/grade-field';
import { MediaDownload, mediaDownloadFragment } from './media-download';
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

const asideTitleCss = css`
  text-transform: uppercase;
  font-size: 1.125rem;
  margin: 0 0 0.5rem;
  font-weight: 500;
  line-height: 1.2;
`;

const downloadLinkCss = css`
  display: block;
  color: inherit;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  &:hover {
    text-decoration: none;
  }
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
      <div
        className={css`
          padding: 16px;
          flex: 1 1 100%;
          overflow-y: auto;
        `}
      >
        {data.awardAssignmentViews.length > 0 && (
          <>
            <h3 className={asideTitleCss}>Awards</h3>
            <div
              className={css`
                padding: 0;
                list-style: none;

                margin-bottom: 16px;
              `}
            >
              {data.awardAssignmentViews.map((v, i) => (
                <div
                  key={i}
                  className={css`
                    margin: 0 -16px;
                    padding: 0 16px;

                    overflow: hidden;

                    display: flex;
                    flex-direction: row;

                    &:nth-of-type(odd) {
                      background-color: rgba(0, 0, 0, 0.05);
                    }

                    &:nth-of-type(even) {
                      background-color: rgba(0, 0, 0, 0.02);
                    }
                  `}
                  title={v.assignment.award.title.variant}
                >
                  <span
                    className={css`
                      overflow: hidden;
                      text-overflow: ellipsis;
                      white-space: nowrap;
                    `}
                  >
                    {v.assignment.award.title.variant}
                  </span>
                  <span
                    className={cx(
                      css`
                        margin-left: auto;
                      `,
                      badgeCss,
                      getBadgeCssByValence(v.gradeField?.valence ?? null),
                    )}
                  >
                    <GradeField data={v.gradeField} />
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
        {data.assignment.problem.attachments.length > 0 && (
          <>
            <h3 className={asideTitleCss}>Attachments</h3>
            <div
              className={css`
                margin-bottom: 16px;
              `}
            >
              {data.assignment.problem.attachments.map((a, i) => (
                <MediaDownload key={i} className={downloadLinkCss} data={a.media} />
              ))}
            </div>
          </>
        )}
        <h2 className={asideTitleCss}>Statement file</h2>
        <MediaDownload className={downloadLinkCss} data={data.assignment.problem.statement} />
      </div>
    </div>
  );
}
