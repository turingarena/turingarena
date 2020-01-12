import { Component, Input, TemplateRef } from '@angular/core';
import { ColDef, ColGroupDef, GridOptions } from 'ag-grid-community';

import { ProblemFragment } from '../../fragments/__generated__/ProblemFragment';
import { VariantService } from '../../variant.service';
import { AdminQuery } from '../__generated__/AdminQuery';

@Component({
  selector: 'app-admin-contestants',
  templateUrl: './admin-contestants.component.html',
  styleUrls: ['./admin-contestants.component.scss'],
})
export class AdminContestantsComponent {

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

  getColumnDefs = (problems: ProblemFragment[], templates: Record<'grading', TemplateRef<unknown>>): Array<ColDef | ColGroupDef> => [
    {
      colId: 'id',
      field: 'id',
      headerName: 'ID',
      checkboxSelection: true,
      headerCheckboxSelection: true,
      filter: true,
    },
    {
      colId: 'displayName',
      field: 'displayName',
      headerName: 'Name',
    },
    ...problems.map((problem, problemIndex): ColGroupDef => ({
      groupId: `problem/${problem.name}`,
      headerName: this.variantService.selectTextVariant(problem.material.title),
      columnGroupShow: 'open',
      children: [
        ...problem.material.awards.map((award, i): ColDef => ({
          colId: `problem/${problem.name}/award/${award.name}`,
          headerName: this.variantService.selectTextVariant(award.material.title),
          field: `problemSetView.problemViews.${problemIndex}.awards.${i}.grading`,
          cellClass: 'grid-cell-grading',
          columnGroupShow: 'open',
          cellRenderer: 'templateCellRenderer',
          cellRendererParams: {
            template: templates.grading,
          },
        })),
        {
          colId: `problem/${problem.name}/evaluation.grading`,
          field: `problemSetView.problemViews.${problemIndex}.grading`,
          cellClass: 'grid-cell-grading',
          headerName: 'Total',
          cellRenderer: 'templateCellRenderer',
          cellRendererParams: {
            template: templates.grading,
          },
        },
      ],
    })),
    {
      colId: 'grading',
      field: 'problemSetView.grading',
      headerName: 'Total',
      cellClass: 'grid-cell-grading',
      columnGroupShow: 'closed',
      cellRenderer: 'templateCellRenderer',
      cellRendererParams: {
        template: templates.grading,
      },
    },
  ]
}
