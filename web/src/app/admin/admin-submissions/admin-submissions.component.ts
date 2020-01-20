import { Component, Input, TemplateRef } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, ColGroupDef, GridOptions } from 'ag-grid-community';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import {
  AdminQuery,
  ProblemFragment,
  ReevaluateMutation,
  ReevaluateMutationVariables,
  SubmissionFragment,
} from '../../../generated/graphql-types';
import { VariantService } from '../../variant.service';

type TemplateName = 'grading' | 'createdAt';

@Component({
  selector: 'app-admin-submissions',
  templateUrl: './admin-submissions.component.html',
  styleUrls: ['./admin-submissions.component.scss'],
})
export class AdminSubmissionsComponent {
  constructor(private readonly apollo: Apollo, private readonly variantService: VariantService) {}

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
      groupId: 'user',
      headerName: 'User',
      children: [
        {
          colId: 'user.id',
          field: 'user.id',
          headerName: 'ID',
          sortable: true,
          filter: true,
        },
        {
          colId: 'user.displayName',
          field: 'user.displayName',
          headerName: 'Name',
          columnGroupShow: 'open',
        },
      ],
    },
    {
      colId: 'problem.name',
      field: 'problem.name',
      headerName: 'Problem',
      sortable: true,
      filter: true,
    },
    {
      colId: 'createdAt',
      field: 'createdAt',
      cellClass: 'grid-cell-grading',
      headerName: 'Submission Time',
      cellRenderer: 'templateCellRenderer',
      cellRendererParams: {
        template: templates.createdAt,
      },
      sortable: true,
      sort: 'desc',
    },
    {
      colId: 'evaluation.status',
      field: 'evaluation.status',
      headerName: 'Evaluation Status',
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
                  valueGetter: ({ data: submissionData }) => {
                    if (submissionData.problem.name !== problem.name) {
                      return undefined;
                    }
                    const submission = submissionData as SubmissionFragment;

                    return submission.evaluation.awards[i].grading;
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
                valueGetter: ({ data: submissionData }) => {
                  if (submissionData.problem.name !== problem.name) {
                    return undefined;
                  }
                  const submission = submissionData as SubmissionFragment;

                  return submission.evaluation.grading;
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
          field: 'evaluation.grading',
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

  async reevaluateSelected(grid: AgGridAngular) {
    const submissionIds: string[] = [];

    grid.api.getSelectedNodes().forEach(({ data }) => {
      submissionIds.push(data.id);
    });

    await this.apollo
      .mutate<ReevaluateMutation, ReevaluateMutationVariables>({
        mutation: gql`
          mutation ReevaluateMutation($submissionIds: [String!]!) {
            evaluate(submissionIds: $submissionIds) {
              ok
            }
          }
        `,
        variables: {
          submissionIds,
        },
        refetchQueries: ['AdminQuery'],
        awaitRefetchQueries: true,
      })
      .toPromise();
  }
}
