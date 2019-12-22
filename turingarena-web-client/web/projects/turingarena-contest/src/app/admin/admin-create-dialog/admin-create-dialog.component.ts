import { Component, Input, ViewChild } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef, RowEvent, RowNode, ValueFormatterParams } from 'ag-grid-community';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { UserInput } from '../../../../../../__generated__/globalTypes';
import { FileLoadService } from '../../file-load.service';

import { AdminCreateMutation, AdminCreateMutationVariables } from './__generated__/AdminCreateMutation';
import { DryImportMutation, DryImportMutationVariables } from './__generated__/DryImportMutation';

const valueFormatter = ({ value, colDef }: ValueFormatterParams) => value ? value : `<${colDef.headerName}>`;

@Component({
  selector: 'app-admin-create-dialog',
  templateUrl: './admin-create-dialog.component.html',
  styleUrls: ['./admin-create-dialog.component.scss'],
})
export class AdminCreateDialogComponent {

  constructor(
    private readonly apollo: Apollo,
    private readonly fileLoadService: FileLoadService,
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
      valueFormatter,
    },
    {
      headerName: 'Display name',
      field: 'displayName',
      editable: true,
      flex: 1,
      singleClickEdit: true,
      valueFormatter,
    },
    {
      headerName: 'Log-in token',
      field: 'token',
      editable: true,
      flex: 1,
      singleClickEdit: true,
      valueFormatter: ({ value, colDef }) => value ? `*`.repeat(value.length) : `<${colDef.headerName}>`,
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

  async importFile(event: Event) {
    const el = event.target as HTMLInputElement;
    const file = el.files![0];
    el.value = '';

    const content = await this.fileLoadService.loadFileContent(file);
    const result = await this.apollo.mutate<DryImportMutation, DryImportMutationVariables>({
      mutation: gql`
        mutation DryImportMutation($input: ImportFileInput!) {
          import(inputs: [$input], dryRun: true) {
            users {
              id
              displayName
              token
            }
          }
        }
      `,
      variables: {
        input: {
          content,
          name: file.name,
          filetype: file.type,
        },
      },
      refetchQueries: ['AdminQuery'],
    }).toPromise();

    const { data } = result;
    if (data !== null && data !== undefined) {
      const t = this.contestantsGrid.api.updateRowData({ add: data.import.users, addIndex: 0 });
      t.add.forEach((node) => { node.setSelected(true); });
    }
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
        contestantInputs: this.getRowData().map(({ id, displayName, token }) => ({ id, displayName, token })),
      },
      refetchQueries: ['AdminQuery'],
    }).toPromise();
    this.modal.close();
  }

}
