import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef, RowNode } from 'ag-grid-community';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { distinctUntilChanged, map, tap } from 'rxjs/operators';

import { AdminQuery } from './__generated__/AdminQuery';
import { ReevaluateSubmissionsMutation, ReevaluateSubmissionsMutationVariables } from './__generated__/ReevaluateSubmissionsMutation';
import { AdminAwardColumnsService } from './admin-award-columns.service';

export class AdminSubmissionGridModel {
  constructor(
    private readonly service: AdminSubmissionsService,
    private readonly adminQuery: QueryRef<AdminQuery>,
    private readonly gridProvider: () => AgGridAngular,
  ) { }

  defaultColDef = {
    sortable: true,
    filter: 'agNumberColumnFilter',
    resizable: true,
    lockPinned: true,
    width: 100,
    enableCellChangeFlash: true,
  };

  columnDefs = this.adminQuery.valueChanges.pipe(
    map(({ data }): (ColDef | ColGroupDef)[] => [
      {
        colId: 'id',
        headerName: 'ID',
        field: 'id',
        cellClass: 'grid-cell-id',
        checkboxSelection: true,
        pinned: true,
        filter: 'agTextColumnFilter',
        sortable: false,
        flex: 1,
      },
      {
        colId: 'userId',
        headerName: 'Contestant',
        cellClass: 'grid-cell-id',
        field: 'userId',
        filter: 'agTextColumnFilter',
        flex: 1,
      },
      ...this.service.awardColumnService.getAwardColumns({
        data,
        scoreGetter: ({ valueGetterParams: { context: { scoreMap }, node: { data: submission } }, problem, award }) => ({
          score: 0,
          badge: false,
          ...scoreMap.get(`${submission.id}/${problem.name}/${award.name}`),
        }),
        badgeGetter: ({ valueGetterParams: { context: { scoreMap }, node: { data: submission } }, problem, award }) => ({
          score: 0,
          badge: false,
          ...scoreMap.get(`${submission.id}/${problem.name}/${award.name}`),
        }),
      }),
    ]),
    distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
  );

  rowData = this.adminQuery.valueChanges.pipe(
    map(({ data }) => data.submissions),
  );

  context = this.adminQuery.valueChanges.pipe(
    map(({ data }) => ({
      scoreMap: new Map(
        data.awards.map(({ awardName, submission: { problemName, id: submissionId }, value }) => [
          `${submissionId}/${problemName}/${awardName}`,
          value,
        ]),
      ),
    })),
    tap(() => {
      this.gridProvider().api.refreshCells();
      this.gridProvider().api.onSortChanged();
    }),
  );

  async reevaluateSelected() {
    const nodes: RowNode[] = [];
    this.gridProvider().api.forEachNode((node) => nodes.push(node));

    await this.service.apollo.mutate<ReevaluateSubmissionsMutation, ReevaluateSubmissionsMutationVariables>({
      mutation: gql`
        mutation ReevaluateSubmissionsMutation($ids: [String!]!) {
          evaluate(submissionIds: $ids) {
            ok
          }
        }
      `,
      variables: {
        ids: nodes.filter((node) => node.isSelected()).map((node) => node.data.id),
      },
      refetchQueries: ['AdminQuery'],
    }).toPromise();
  }
}

@Injectable({
  providedIn: 'root',
})
export class AdminSubmissionsService {

  constructor(
    readonly awardColumnService: AdminAwardColumnsService,
    readonly apollo: Apollo,
  ) { }

  createGridModel(gridProvider: () => AgGridAngular, adminQuery: QueryRef<AdminQuery>) {
    return new AdminSubmissionGridModel(this, adminQuery, gridProvider);
  }
}
