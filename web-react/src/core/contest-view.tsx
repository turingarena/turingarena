import { gql } from '@apollo/client';
import React from 'react'
import { Route, Switch } from 'react-router-dom';
import { contestProblemAssignmentViewAsideFragment } from './contest-problem-assignment-view-aside';
import { contestViewAsideFragment } from './contest-view-aside';
import { mediaInlineFragment } from './media-inline';
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

export function ContestView() {
  return (
    <Switch>
      <Route path="/:problem">
        <h1>Problem</h1>
      </Route>
      <Route path="/">
        <h1>Contest view</h1>
      </Route>
    </Switch>
  );
}
