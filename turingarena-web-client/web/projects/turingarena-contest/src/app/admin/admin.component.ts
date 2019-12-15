import { Component, ElementRef, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { first, map, tap } from 'rxjs/operators';

import { AwardFragment } from '../__generated__/AwardFragment';
import { AwardOutcomeFragment } from '../__generated__/AwardOutcomeFragment';
import { awardOutcomeFragment } from '../awards';
import { problemMaterialFragment } from '../material';
import { VariantService } from '../variant.service';

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
    private readonly variantService: VariantService,
    readonly route: ActivatedRoute,
  ) { }

  @ViewChild('usersGrid', { static: false })
  usersGrid!: AgGridAngular;

  @ViewChild('submissionsGrid', { static: false })
  submissionsGrid!: AgGridAngular;

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

      fragment AdminSubmissionFragment on Submission {
        id
        problemName
        userId
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
        submissions {
          ...AdminSubmissionFragment
        }
      }
      ${awardOutcomeFragment}
      ${problemMaterialFragment}
    `,
    variables: {},
    pollInterval: 3000,
  });

  defaultColDef: ColDef = {
    sortable: true,
    filter: 'agNumberColumnFilter',
    resizable: true,
    lockPinned: true,
    width: 100,
    enableCellChangeFlash: true,
  };

  usersColumnDefs = this.adminQuery.valueChanges.pipe(
    map(({ data }): (ColDef | ColGroupDef)[] => [
      {
        headerName: 'ID',
        field: 'id',
        checkboxSelection: true,
        pinned: true,
        filter: 'agTextColumnFilter',
        width: 100,
        enableCellChangeFlash: true,
      },
      {
        headerName: 'Name',
        field: 'displayName',
        filter: 'agTextColumnFilter',
        editable: true,
        width: 200,
        enableCellChangeFlash: true,
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
      ...this.getAwardColumns(data),
    ]),
    first(),
  );

  usersRowData = this.adminQuery.valueChanges.pipe(
    map(({ data }) => data.users),
  );

  usersContext = this.adminQuery.valueChanges.pipe(
    map(({ data }) => ({
      scoreMap: new Map(
        data.awards.map(({ awardName, submission: { problemName, userId }, value }) => [
          `${userId}/${problemName}/${awardName}`,
          value,
        ]),
      ),
    })),
    tap(() => {
      this.usersGrid.api.refreshCells();
      this.usersGrid.api.onSortChanged();
    }),
  );

  submissionsColumnDefs = this.adminQuery.valueChanges.pipe(
    map(({ data }): (ColDef | ColGroupDef)[] => [
      {
        headerName: 'ID',
        field: 'id',
        checkboxSelection: true,
        pinned: true,
        filter: 'agTextColumnFilter',
        width: 100,
        enableCellChangeFlash: true,
      },
      ...this.getAwardColumns(data),
    ]),
    first(),
  );

  submissionsRowData = this.adminQuery.valueChanges.pipe(
    map(({ data }) => data.submissions),
  );

  submissionsContext = this.adminQuery.valueChanges.pipe(
    map(({ data }) => ({
      scoreMap: new Map(
        data.awards.map(({ awardName, submission: { problemName, userId }, value }) => [
          `${userId}/${problemName}/${awardName}`,
          value,
        ]),
      ),
    })),
    tap(() => {
      this.submissionsGrid.api.refreshCells();
      this.submissionsGrid.api.onSortChanged();
    }),
  );

  private getAwardColumns(data: AdminQuery): (ColDef | ColGroupDef)[] {
    const awardGetter = ({ scoreMap, user, problem, award }: {
      scoreMap: Map<string, AwardOutcomeFragment['value']>;
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
        headerName: 'Score',
        openByDefault: true,
        children: [
          ...data.problems.map((problem): ColGroupDef => ({
            headerName: this.variantService.selectTextVariant(problem.material.title),
            columnGroupShow: 'open',
            children: [
              ...problem.material.awards.map((award): ColDef => ({
                headerName: this.variantService.selectTextVariant(award.title),
                valueGetter: ({ node: { data: user }, context: { scoreMap } }) =>
                  awardGetter({ scoreMap, user, problem, award })[
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
                headerName: 'Problem',
                valueGetter: ({ node: { data: user }, context: { scoreMap } }) => problem.material.awards
                  .map((award) => awardGetter({ scoreMap, user, problem, award }).score)
                  .reduce((a, b) => a + b, 0),
              },
            ],
          })),
          {
            headerName: 'Total',
            valueGetter: ({ node: { data: user }, context: { scoreMap } }) => data.problems.map((problem) =>
              problem.material.awards
                .map((award) => awardGetter({ scoreMap, user, problem, award }).score)
                .reduce((a, b) => a + b, 0),
            ).reduce((a, b) => a + b, 0),
          },
        ],
      },
    ];
  }

}
