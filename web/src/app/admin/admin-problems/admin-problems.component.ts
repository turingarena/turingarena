import { Component, Input } from '@angular/core';
import { ColDef, ColGroupDef, GridOptions } from 'ag-grid-community';
import { VariantService } from '../../variant.service';
import { AdminQuery } from '../__generated__/AdminQuery';

@Component({
  selector: 'app-admin-problems',
  templateUrl: './admin-problems.component.html',
  styleUrls: ['./admin-problems.component.scss'],
})
export class AdminProblemsComponent {
  constructor(private readonly variantService: VariantService) {}

  @Input()
  data!: AdminQuery;

  gridOptions: GridOptions = {
    getRowNodeId: data => data.name,
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
      colId: 'name',
      field: 'name',
      headerName: 'Name',
      checkboxSelection: true,
      headerCheckboxSelection: true,
      filter: true,
    },
    {
      colId: 'material.title',
      headerName: 'Title',
      sortable: true,
      filter: true,
      valueGetter: ({ data }) => this.variantService.selectTextVariant(data.material.title),
    },
  ];
}
