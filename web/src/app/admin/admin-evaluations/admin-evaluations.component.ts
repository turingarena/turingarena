import { Component, Input, TemplateRef } from '@angular/core';
import { ColDef, ColGroupDef, GridOptions } from 'ag-grid-community';
import { ProblemFragment } from '../../fragments/__generated__/ProblemFragment';
import { VariantService } from '../../variant.service';
import { AdminEvaluationFragment } from '../__generated__/AdminEvaluationFragment';
import { AdminQuery } from '../__generated__/AdminQuery';

export type TemplateName = 'grading' | 'createdAt';

@Component({
  selector: 'app-admin-evaluations',
  templateUrl: './admin-evaluations.component.html',
  styleUrls: ['./admin-evaluations.component.scss'],
})
export class AdminEvaluationsComponent {
  // FIXME: a lot of copy'n'paste here!

  constructor(private readonly variantService: VariantService) {}

  @Input()
  data!: AdminQuery;

  gridOptions: GridOptions = {
    getRowNodeId: data => data.id,
    defaultColDef: {
      resizable: true,
      flex: 1,
    },
    animateRows: true,
    domLayout: 'autoHeight',
    enableCellChangeFlash: true,
  };

  getColumnDefs = (
    problems: ProblemFragment[],
    templates: Record<TemplateName, TemplateRef<unknown>>,
  ): Array<ColDef | ColGroupDef> => [
    {
      colId: 'id',
      field: 'id',
      headerName: 'ID',
      checkboxSelection: true,
      headerCheckboxSelection: true,
      filter: true,
    },
    {
      colId: 'submission.id',
      field: 'submission.id',
      headerName: 'Submission',
      filter: true,
    },
    {
      colId: 'submission.problem.name',
      field: 'submission.problem.name',
      headerName: 'Problem',
      sortable: true,
      filter: true,
    },
    {
      colId: 'createdAt',
      field: 'createdAt',
      cellClass: 'grid-cell-grading',
      headerName: 'Evaluation Time',
      cellRenderer: 'templateCellRenderer',
      cellRendererParams: {
        template: templates.createdAt,
      },
      sortable: true,
      sort: 'desc',
    },
    {
      colId: 'status',
      field: 'status',
      headerName: 'Status',
      sortable: true,
      filter: true,
    },
    {
      groupId: 'grading',
      headerName: 'Grading',
      children: [
        ...problems.map(
          (problem): ColGroupDef => ({
            groupId: `problem/${problem.name}`,
            headerName: this.variantService.selectTextVariant(problem.material.title),
            columnGroupShow: 'open',
            children: [
              ...problem.material.awards.map(
                (award, i): ColDef => ({
                  colId: `problem/${problem.name}/award/${award.name}`,
                  headerName: this.variantService.selectTextVariant(award.material.title),
                  valueGetter: ({ data: evaluationData }) => {
                    const evaluation = evaluationData as AdminEvaluationFragment;
                    if (evaluationData.submission.problem.name !== problem.name) {
                      return undefined;
                    }

                    return evaluation.awards[i].grading;
                  },
                  cellClass: 'grid-cell-grading',
                  columnGroupShow: 'open',
                  cellRenderer: 'templateCellRenderer',
                  cellRendererParams: {
                    template: templates.grading,
                  },
                }),
              ),
              {
                colId: `problem/${problem.name}/evaluation.grading`,
                valueGetter: ({ data: evaluationData }) => {
                  const evaluation = evaluationData as AdminEvaluationFragment;
                  if (evaluationData.submission.problem.name !== problem.name) {
                    return undefined;
                  }

                  return evaluation.grading;
                },
                headerName: 'Total',
                cellClass: 'grid-cell-grading',
                columnGroupShow: 'open',
                cellRenderer: 'templateCellRenderer',
                cellRendererParams: {
                  template: templates.grading,
                },
              },
            ],
          }),
        ),
        {
          colId: 'evaluation',
          field: 'grading',
          headerName: 'Total',
          cellClass: 'grid-cell-grading',
          columnGroupShow: 'closed',
          cellRenderer: 'templateCellRenderer',
          cellRendererParams: {
            template: templates.grading,
          },
        },
      ],
    },
  ];
}
