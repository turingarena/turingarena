import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { Route, Switch } from 'react-router-dom';
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
  return (
    <div
      className={css`
        flex: 1;

        display: flex;
        flex-direction: row;
      `}
    >
      <ContestViewAside data={data} />
      <Switch>
        {data.problemSetView !== null &&
          data.problemSetView.assignmentViews.map(a => (
            <Route key={a.assignment.problem.id} path={`/${a.assignment.problem.name}`}>
              <ContestProblemAssignmentViewAside data={a} />
              <MediaInline data={a.assignment.problem.statement} />
            </Route>
          ))}
        <Route exact path="/">
          <MediaInline data={data.contest.statement} />
        </Route>
      </Switch>
    </div>
  );
}
