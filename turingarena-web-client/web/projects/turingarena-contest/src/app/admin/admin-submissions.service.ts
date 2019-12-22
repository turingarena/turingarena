import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { QueryRef } from 'apollo-angular';
import { first, map, tap } from 'rxjs/operators';

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
            headerName: 'ID',
            field: 'id',
            checkboxSelection: true,
            pinned: true,
            filter: 'agTextColumnFilter',
            width: 100,
            enableCellChangeFlash: true,
          },
          ...this.awardColumnService.getAwardColumns(data),
        ]),
        first(),
      ),
      rowData: adminQuery.valueChanges.pipe(
        map(({ data }) => data.submissions),
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
