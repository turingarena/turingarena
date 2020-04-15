import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { ContestViewFragment } from '../generated/graphql-types';
import { hiddenCss } from '../util/components/hidden';
import { FragmentProps } from '../util/fragment-props';
import { PathRouter } from '../util/paths';
import {
  ContestProblemAssignmentViewAside,
  contestProblemAssignmentViewAsideFragment,
} from './contest-problem-assignment-view-aside';
import { ContestViewAside, contestViewAsideFragment } from './contest-view-aside';
import { MediaInline, mediaInlineFragment } from './media-inline';
import { textFragment } from './text';

export const contestViewFragment = gql`
  fragment ContestView on ContestView {
    contest {
      id
      title {
        ...Text
      }
      statement {
        ...MediaInline
      }
    }

    problemSetView {
      assignmentViews {
        assignment {
          id
          problem {
            id
            name
            statement {
              ...MediaInline
            }
          }
        }
        ...ContestProblemAssignmentViewAside
      }
    }

    ...ContestViewAside
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${contestViewAsideFragment}
  ${contestProblemAssignmentViewAsideFragment}
`;

const activeMediaInlineCss = css`
  flex: 1;
  overflow: hidden;
`;

export function ContestView({ data }: FragmentProps<ContestViewFragment>) {
  return (
    <div
      className={css`
        flex: 1 1 0;

        display: flex;
        flex-direction: row;
        overflow: hidden;
      `}
    >
      <ContestViewAside data={data} />
      {data.problemSetView !== null &&
        data.problemSetView.assignmentViews.map(a => (
          <PathRouter key={a.assignment.problem.id} path={`/${a.assignment.problem.name}`}>
            {({ match }) => (
              <>
                <ContestProblemAssignmentViewAside className={match !== null ? undefined : hiddenCss} data={a} />
                <div className={match !== null ? activeMediaInlineCss : hiddenCss}>
                  <MediaInline data={a.assignment.problem.statement} />
                </div>
              </>
            )}
          </PathRouter>
        ))}
      <PathRouter path="/" exact>
        {({ match }) => (
          <div className={match !== null ? activeMediaInlineCss : hiddenCss}>
            <MediaInline data={data.contest.statement} />
          </div>
        )}
      </PathRouter>
    </div>
  );
}
