import { Injectable } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { QueryRef } from 'apollo-angular';
import { first, map, tap } from 'rxjs/operators';

import { ProblemFragment } from '../__generated__/ProblemFragment';
import { VariantService } from '../variant.service';

import { AdminQuery } from './__generated__/AdminQuery';

@Injectable({
  providedIn: 'root',
})
export class AdminProblemsService {

  constructor(
    private readonly variantService: VariantService,
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
        map((): (ColDef | ColGroupDef)[] => [
          {
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
            headerName: 'Title',
            filter: 'agTextColumnFilter',
            width: 200,
            valueGetter: ({ node: { data: problem } }) =>
              this.variantService.selectTextVariant((problem as ProblemFragment).material.title),
          },
        ]),
        first(),
      ),
      rowData: adminQuery.valueChanges.pipe(
        map(({ data }) => data.problems),
      ),
      context: adminQuery.valueChanges.pipe(
        tap(() => {
          gridProvider().api.refreshCells();
          gridProvider().api.onSortChanged();
        }),
      ),
    };
  }
}
