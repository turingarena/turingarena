import { Component, Input, ViewChild } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { UserInput } from '../../../../../../__generated__/globalTypes';

import { AdminCreateMutation, AdminCreateMutationVariables } from './__generated__/AdminCreateMutation';
import { ColDef, CellEditingStartedEvent, CellEditingStoppedEvent, CellValueChangedEvent, CellEvent, RowEvent, RowNode, ICellRendererParams, ValueFormatterParams } from 'ag-grid-community';
import { AgGridAngular } from 'ag-grid-angular';

@Component({
  selector: 'app-admin-create-dialog',
  templateUrl: './admin-create-dialog.component.html',
  styleUrls: ['./admin-create-dialog.component.scss'],
})
export class AdminCreateDialogComponent {

  constructor(
    private readonly apollo: Apollo,
  ) { }

  @Input()
  modal!: NgbActiveModal;

  @ViewChild('contestantsGrid', { static: false })
  contestantsGrid!: AgGridAngular;

  contestantInputs: UserInput[] = [this.makeNewContestantInput()];

  contestantsColumnDefs: ColDef[] = [
    {
      headerName: 'Add?',
      editable: false,
      checkboxSelection: true,
      width: 60,
      pinned: true,
      lockPinned: true,
      resizable: false,
    },
    {
      headerName: 'ID',
      field: 'id',
      editable: true,
      flex: 1,
      singleClickEdit: true,
      valueFormatter: ({ value, colDef }: ValueFormatterParams) => value ? value : `<add ${colDef.headerName}>`,
    },
    {
      headerName: 'Display name',
      field: 'displayName',
      editable: true,
      flex: 1,
      singleClickEdit: true,
    },
    {
      headerName: 'Log-in token',
      field: 'token',
      editable: true,
      flex: 1,
      singleClickEdit: true,
    },
  ];

  isRowEmpty(node: RowNode) {
    return ['id', 'displayName', 'token'].every((key) => !node.data[key]);
  }

  onRowEditingStarted(event: RowEvent) {
    event.node.setSelected(true);
    if (event.rowIndex === event.api.getModel().getRowCount() - 1) {
      event.api.updateRowData({
        add: [this.makeNewContestantInput()],
      });
    }
  }

  onRowEditingStopped(event: RowEvent) {
    if (this.isRowEmpty(event.node)) {
      event.node.setSelected(false);
      if (event.rowIndex !== event.api.getModel().getRowCount() - 1) {
        event.api.updateRowData({
          remove: [event.data],
        });
      }
    }
  }

  private makeNewContestantInput(): UserInput {
    return {
      id: '',
      displayName: '',
      token: '',
    };
  }

  private getRowData() {
    const rowData: UserInput[] = [];
    this.contestantsGrid.api.forEachNode((node) => {
      if (node.isSelected()) {
        rowData.push(node.data);
      }
    });

    return rowData;
  }

  async submit() {
    await this.apollo.mutate<AdminCreateMutation, AdminCreateMutationVariables>({
      mutation: gql`
        mutation AdminCreateMutation($contestantInputs: [UserInput!]!) {
          addUsers(inputs: $contestantInputs) {
            ok
          }
        }
      `,
      variables: {
        contestantInputs: this.getRowData(),
      },
    }).toPromise();
    this.modal.close();
  }

}
