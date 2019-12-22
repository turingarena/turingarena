import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef, RowNode } from 'ag-grid-community';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { first, map, tap } from 'rxjs/operators';

import { AdminQuery } from './__generated__/AdminQuery';
import { DeleteUsersMutation, DeleteUsersMutationVariables } from './__generated__/DeleteUsersMutation';
import { UpdateUserMutation, UpdateUserMutationVariables } from './__generated__/UpdateUserMutation';
import { AdminAwardColumnsService } from './admin-award-columns.service';

export class AdminContestantGridModel {
  constructor(
    readonly service: AdminContestantsService,
    readonly gridProvider: () => AgGridAngular,
    readonly adminQuery: QueryRef<AdminQuery>,
  ) { }

  defaultColDef = {
    sortable: true,
    filter: 'agNumberColumnFilter',
    resizable: true,
    lockPinned: true,
    width: 100,
    enableCellChangeFlash: true,
    flex: 1,
  };

  columnDefs = this.adminQuery.valueChanges.pipe(
    map(({ data }): (ColDef | ColGroupDef)[] => [
      {
        headerName: 'ID',
        field: 'id',
        headerCheckboxSelection: true,
        checkboxSelection: true,
        pinned: true,
        filter: 'agTextColumnFilter',
        width: 100,
        enableCellChangeFlash: true,
        flex: 1,
      },
      {
        headerName: 'Name',
        field: 'displayName',
        filter: 'agTextColumnFilter',
        editable: true,
        width: 200,
        flex: 2,
        enableCellChangeFlash: true,
        valueSetter: ({ newValue, node: { data: user } }) => {
          this.service.apollo.mutate<UpdateUserMutation, UpdateUserMutationVariables>({
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
      ...this.service.awardColumnService.getAwardColumns({
        data,
        scoreGetter: ({ valueGetterParams: { context: { scoreMap }, node: { data: user } }, problem, award }) => ({
          score: 0,
          badge: false,
          ...scoreMap.get(`${user.id}/${problem.name}/${award.name}`),
        }),
        badgeGetter: ({ valueGetterParams: { context: { scoreMap }, node: { data: user } }, problem, award }) => ({
          score: 0,
          badge: false,
          ...scoreMap.get(`${user.id}/${problem.name}/${award.name}`),
        }),
      }),
    ]),
    first(),
  );

  rowData = this.adminQuery.valueChanges.pipe(
    map(({ data }) => data.users),
  );

  context = this.adminQuery.valueChanges.pipe(
    map(({ data }) => ({
      scoreMap: new Map(
        data.awards.map(({ awardName, submission: { problemName, userId }, value }) => [
          `${userId}/${problemName}/${awardName}`,
          value,
        ]),
      ),
    })),
    tap(() => {
      this.gridProvider().api.refreshCells();
      this.gridProvider().api.onSortChanged();
    }),
  );

  async deleteSelected() {
    const nodes: RowNode[] = [];
    this.gridProvider().api.forEachNode((node) => nodes.push(node));

    await this.service.apollo.mutate<DeleteUsersMutation, DeleteUsersMutationVariables>({
      mutation: gql`
        mutation DeleteUsersMutation($ids: [String!]!) {
          deleteUsers(ids: $ids) {
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
export class AdminContestantsService {
  constructor(
    readonly apollo: Apollo,
    readonly awardColumnService: AdminAwardColumnsService,
  ) { }

  createGridModel(gridProvider: () => AgGridAngular, adminQuery: QueryRef<AdminQuery>) {
    return new AdminContestantGridModel(this, gridProvider, adminQuery);
  }
}
