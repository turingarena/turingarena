import { Component, Input } from '@angular/core';
import { ColDef, ColGroupDef } from 'ag-grid-community';
import { Apollo } from 'apollo-angular';

import { ProblemFragment } from '../../fragments/__generated__/ProblemFragment';
import { SubmissionFragment } from '../../fragments/__generated__/SubmissionFragment';
import { VariantService } from '../../variant.service';
import { AdminQuery } from '../__generated__/AdminQuery';

@Component({
  selector: 'app-admin-submissions',
  templateUrl: './admin-submissions.component.html',
  styleUrls: ['./admin-submissions.component.scss'],
})
export class AdminSubmissionsComponent {

  constructor(
    private readonly apollo: Apollo,
    private readonly variantService: VariantService,
  ) { }

  @Input()
  data!: AdminQuery;

  getColumnDefs = (problems: ProblemFragment[]): Array<ColDef | ColGroupDef> => [
    {
      colId: 'id',
      field: 'id',
      headerName: 'ID',
      flex: 1,
      checkboxSelection: true,
      headerCheckboxSelection: true,
    },
    {
      groupId: 'user',
      headerName: 'User',
      children: [
        {
          colId: 'user.id',
          field: 'user.id',
          headerName: 'ID',
          flex: 1,
        },
        {
          colId: 'user.displayName',
          field: 'user.displayName',
          headerName: 'Name',
          flex: 2,
          columnGroupShow: 'open',
        },
      ],
    },
    {
      colId: 'problem.name',
      field: 'problem.name',
      headerName: 'Name',
      flex: 1,
    },
    {
      colId: 'createdAt',
      field: 'createdAt',
      headerName: 'Submission Time',
      flex: 2,
    },
    {
      colId: 'evaluation.status',
      field: 'evaluation.status',
      headerName: 'Evaluation Status',
      flex: 1,
    },
    {
      groupId: 'grading',
      headerName: 'Grading',
      children: [
        ...problems.map((problem): ColGroupDef => ({
          groupId: `problem/${problem.name}`,
          headerName: this.variantService.selectTextVariant(problem.material.title),
          columnGroupShow: 'open',
          children: [
            ...problem.material.awards.map((award, i): ColDef => ({
              colId: `problem/${problem.name}/award/${award.name}`,
              headerName: this.variantService.selectTextVariant(award.material.title),
              flex: 1,
              valueGetter: ({ data: submissionData }) => {
                if (submissionData.problem.name !== problem.name) { return undefined; }
                const submission = submissionData as SubmissionFragment;

                return submission.evaluation.awards[i].grading;
              },
              columnGroupShow: 'open',
            })),
            {
              colId: `problem/${problem.name}/evaluation.grading`,
              valueGetter: ({ data: submissionData }) => {
                if (submissionData.problem.name !== problem.name) { return undefined; }
                const submission = submissionData as SubmissionFragment;

                return submission.evaluation.grading;
              },
              columnGroupShow: 'open',
              flex: 1,
            },
          ],
        })),
        {
          colId: 'evaluation',
          field: 'evaluation.grading',
          headerName: 'Total',
          flex: 1,
          columnGroupShow: 'closed',
        },
      ],
    },
  ]

}
