import { Component, Input } from '@angular/core';
import { ColDef, ColGroupDef, GridOptions } from 'ag-grid-community';

import { VariantService } from '../../variant.service';
import { AdminQuery } from '../__generated__/AdminQuery';

@Component({
  selector: 'app-admin-messages',
  templateUrl: './admin-messages.component.html',
  styleUrls: ['./admin-messages.component.scss'],
})
export class AdminMessagesComponent {

  constructor(
    private readonly variantService: VariantService,
  ) { }

  @Input()
  data!: AdminQuery;

  gridOptions: GridOptions = {
    getRowNodeId: (data) => data.id,
    defaultColDef: {
      resizable: true,
      flex: 1,
    },
    animateRows: true,
    domLayout: 'autoHeight',
    enableCellChangeFlash: true,
  };

  columnDefs: Array<ColDef | ColGroupDef> = [
    {
      colId: 'id',
      field: 'id',
      headerName: 'ID',
      checkboxSelection: true,
      headerCheckboxSelection: true,
      filter: true,
    },
    {
      colId: 'createdAt',
      field: 'createdAt',
      headerName: 'Time',
      filter: true,
      sortable: true,
      sort: 'desc',
    },
    {
      colId: 'user.id',
      field: 'user.id',
      headerName: 'User',
      filter: true,
      sortable: true,
    },
    {
      colId: 'kind',
      field: 'kind',
      headerName: 'Kind',
      filter: true,
      sortable: true,
    },
    {
      colId: 'text',
      field: 'text',
      headerName: 'Text',
      filter: true,
    },
  ];

}
