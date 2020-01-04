import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef, RowNode } from 'ag-grid-community';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { distinctUntilChanged, map, tap } from 'rxjs/operators';

import { VariantService } from '../variant.service';

import { AdminProblemFragment } from './__generated__/AdminProblemFragment';
import { AdminQuery } from './__generated__/AdminQuery';
import { DeleteProblemsMutation, DeleteProblemsMutationVariables } from './__generated__/DeleteProblemsMutation';

export class AdminProblemGridModel {
  constructor(
    private readonly service: AdminProblemsService,
    private readonly gridProvider: () => AgGridAngular,
    private readonly adminQuery: QueryRef<AdminQuery>,
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
    map((): (ColDef | ColGroupDef)[] => [
      {
        colId: 'name',
        headerName: 'Name',
        field: 'name',
        checkboxSelection: true,
        pinned: true,
        filter: 'agTextColumnFilter',
        width: 200,
        enableCellChangeFlash: true,
        rowDrag: true,
      },
      {
        colId: 'title',
        headerName: 'Title',
        filter: 'agTextColumnFilter',
        width: 200,
        valueGetter: ({ node: { data: problem } }) =>
          this.service.variantService.selectTextVariant((problem as AdminProblemFragment).material.title),
      },
    ]),
    distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
  );

  rowData = this.adminQuery.valueChanges.pipe(
    map(({ data }) => data.contest.problems),
  );

  context = this.adminQuery.valueChanges.pipe(
    tap(() => {
      this.gridProvider().api.refreshCells();
      this.gridProvider().api.onSortChanged();
    }),
  );


  async deleteSelected() {
    const nodes: RowNode[] = [];
    this.gridProvider().api.forEachNode((node) => nodes.push(node));

    await this.service.apollo.mutate<DeleteProblemsMutation, DeleteProblemsMutationVariables>({
      mutation: gql`
        mutation DeleteProblemsMutation($names: [String!]!) {
          deleteProblems(names: $names) {
            ok
          }
        }
      `,
      variables: {
        names: nodes.filter((node) => node.isSelected()).map((node) => node.data.name),
      },
      refetchQueries: ['AdminQuery'],
    }).toPromise();
  }
}

@Injectable({
  providedIn: 'root',
})
export class AdminProblemsService {

  constructor(
    readonly variantService: VariantService,
    readonly apollo: Apollo,
  ) { }

  createGridModel(gridProvider: () => AgGridAngular, adminQuery: QueryRef<AdminQuery>) {
    return new AdminProblemGridModel(this, gridProvider, adminQuery);
  }
}
