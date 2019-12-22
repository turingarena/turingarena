import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { QueryRef } from 'apollo-angular';
import { distinctUntilChanged, map, tap } from 'rxjs/operators';

import { AdminQuery } from './__generated__/AdminQuery';
import { AdminAwardColumnsService } from './admin-award-columns.service';

@Injectable({
  providedIn: 'root',
})
export class AdminSubmissionsService {

  constructor(
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
      },
      columnDefs: adminQuery.valueChanges.pipe(
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
          ...this.awardColumnService.getAwardColumns({
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
      ),
      rowData: adminQuery.valueChanges.pipe(
        map(({ data }) => data.submissions),
      ),
      context: adminQuery.valueChanges.pipe(
        map(({ data }) => ({
          scoreMap: new Map(
            data.awards.map(({ awardName, submission: { problemName, id: submissionId }, value }) => [
              `${submissionId}/${problemName}/${awardName}`,
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
