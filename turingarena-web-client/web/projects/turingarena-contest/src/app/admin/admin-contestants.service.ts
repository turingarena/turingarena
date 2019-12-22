import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { first, map, tap } from 'rxjs/operators';

import { AdminQuery } from './__generated__/AdminQuery';
import { UpdateUserMutation, UpdateUserMutationVariables } from './__generated__/UpdateUserMutation';
import { AdminAwardColumnsService } from './admin-award-columns.service';

@Injectable({
  providedIn: 'root',
})
export class AdminContestantsService {

  constructor(
    private readonly apollo: Apollo,
    private readonly awardColumnService: AdminAwardColumnsService,
  ) { }

  createGridModel(gridProvider: () => AgGridAngular, adminQuery: QueryRef<AdminQuery>) {
    return {
      defaultColDef: {
        sortable: true,
        filter: 'agNumberColumnFilter',
        resizable: true,
        lockPinned: true,
        width: 100,
        enableCellChangeFlash: true,
        flex: 1,
      },
      columnDefs: adminQuery.valueChanges.pipe(
        map(({ data }): (ColDef | ColGroupDef)[] => [
          {
            headerName: 'ID',
            field: 'id',
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
          ...this.awardColumnService.getAwardColumns({
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
      ),
      rowData: adminQuery.valueChanges.pipe(
        map(({ data }) => data.users),
      ),
      context: adminQuery.valueChanges.pipe(
        map(({ data }) => ({
          scoreMap: new Map(
            data.awards.map(({ awardName, submission: { problemName, userId }, value }) => [
              `${userId}/${problemName}/${awardName}`,
              value,
            ]),
          ),
        })),
        tap(() => {
          gridProvider().api.refreshCells();
          gridProvider().api.onSortChanged();
        }),
      ),
    };
  }
}
