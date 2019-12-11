import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { first, map } from 'rxjs/operators';

import { AwardFragment } from '../__generated__/AwardFragment';
import { awardOutcomeFragment } from '../awards';
import { problemMaterialFragment } from '../material';

import { AdminProblemFragment } from './__generated__/AdminProblemFragment';
import { AdminQuery } from './__generated__/AdminQuery';
import { AdminUserFragment } from './__generated__/AdminUserFragment';
import { UpdateUserMutation, UpdateUserMutationVariables } from './__generated__/UpdateUserMutation';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent {

  constructor(
    private readonly apollo: Apollo,
    readonly route: ActivatedRoute,
  ) { }

  quickFilterText = '';

  adminQuery = this.apollo.watchQuery<AdminQuery>({
    query: gql`
      fragment AdminProblemFragment on Problem {
        name
        material {
          ...MaterialFragment
        }
      }

      fragment AdminUserFragment on User {
        id
        displayName
      }

      fragment AdminAwardFragment on AwardOutcome {
        submission {
          problemName
          userId
        }
        ...AwardOutcomeFragment
      }

      query AdminQuery {
        serverTime
        problems {
          ...AdminProblemFragment
        }
        users {
          ...AdminUserFragment
        }
        awards {
          ...AdminAwardFragment
        }
      }
      ${awardOutcomeFragment}
      ${problemMaterialFragment}
    `,
    variables: {},
    pollInterval: 10000,
  });

  defaultColDef: ColDef = {
    sortable: true,
    filter: 'agNumberColumnFilter',
    resizable: true,
    lockPinned: true,
  };

  columnDefs = this.adminQuery.valueChanges.pipe(
    map(({ data }): (ColDef | ColGroupDef)[] => {
      const scoreMap = new Map(
        data.awards.map(({ awardName, submission: { problemName, userId }, value }) => [
          `${userId}/${problemName}/${awardName}`,
          value,
        ]),
      );

      const awardGetter = ({ user, problem, award }: {
        user: AdminUserFragment;
        problem: AdminProblemFragment;
        award: AwardFragment;
      }) => ({
        score: 0,
        badge: false,
        ...scoreMap.get(`${user.id}/${problem.name}/${award.name}`),
      });

      return [
        {
          headerName: 'ID',
          field: 'id',
          checkboxSelection: true,
          pinned: true,
          filter: 'agTextColumnFilter',
        },
        {
          headerName: 'Name',
          field: 'displayName',
          filter: 'agTextColumnFilter',
          editable: true,
          valueSetter: ({ newValue, node: { data: user } }) => {
            this.apollo.mutate<UpdateUserMutation, UpdateUserMutationVariables>({
              mutation: gql`
                mutation UpdateUserMutation($input: UserUpdateInput!) {
                  updateUsers(inputs: [$input]) {
                    ok
                  }
                }
              `,
              variables: {
                input: {
                  id: user.id,
                  displayName: newValue,
                },
              },
              refetchQueries: ['AdminQuery'],
            }).subscribe();

            return true;
          },
        },
        {
          headerName: 'Score',
          children: [
            ...data.problems.map((problem): ColGroupDef => ({
              headerName: problem.name,
              columnGroupShow: 'open',
              children: [
                ...problem.material.awards.map((award): ColDef => ({
                  headerName: award.name,
                  valueGetter: ({ node: { data: user } }) => awardGetter({ user, problem, award })[
                    award.content.__typename === 'ScoreAwardContent' ? 'score' : 'badge'
                  ],
                  valueFormatter:
                    award.content.__typename === 'ScoreAwardContent'
                      ? ({ value }) => value
                      : ({ value }) => value ? 'yes' : 'no'
                  ,
                  columnGroupShow: 'open',
                })),
                {
                  headerName: 'Problem total',
                  valueGetter: ({ node: { data: user } }) => problem.material.awards
                    .map((award) => awardGetter({ user, problem, award }).score)
                    .reduce((a, b) => a + b, 0),
                },
              ],
            })),
            {
              headerName: 'Total',
              valueGetter: ({ node: { data: user } }) => data.problems.map((problem) =>
                problem.material.awards
                  .map((award) => awardGetter({ user, problem, award }).score)
                  .reduce((a, b) => a + b, 0),
              ).reduce((a, b) => a + b, 0),
            },
          ],
        },
      ];
    }),
    first(),
  );

  rowData = this.adminQuery.valueChanges.pipe(
    map(({ data }) => data.users),
  );

}
