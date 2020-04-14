import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { useRouteMatch } from 'react-router-dom';
import { ContestViewFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
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

export function ContestView({ data }: FragmentProps<ContestViewFragment>) {
  const problem = useRouteMatch<{ problemName: string }>('/:problemName');

  return (
    <div
      className={css`
        flex: 1;

        display: flex;
        flex-direction: row;
      `}
    >
      <ContestViewAside data={data} />
      {data.problemSetView !== null &&
        data.problemSetView.assignmentViews.map(a => (
          <div
            key={a.assignment.problem.id}
            className={
              problem !== null && problem.params.problemName === a.assignment.problem.name
                ? css`
                    display: flex;
                    flex: 1;
                  `
                : css`
                    display: none;
                  `
            }
          >
            <ContestProblemAssignmentViewAside data={a} />
            <MediaInline data={a.assignment.problem.statement} />
          </div>
        ))}
      <div
        className={
          problem === null
            ? css`
                display: flex;
                flex: 1;
              `
            : css`
                display: none;
              `
        }
      >
        <MediaInline data={data.contest.statement} />
      </div>
    </div>
  );
}
