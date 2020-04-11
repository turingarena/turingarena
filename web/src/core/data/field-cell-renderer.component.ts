import { Component, ViewEncapsulation } from '@angular/core';
import { ICellRendererAngularComp } from 'ag-grid-angular';
import { ICellRendererParams } from 'ag-grid-community';
import { FieldFragment } from '../../generated/graphql-types';

export type FieldCellRendererParams = ICellRendererParams & { field: FieldFragment };

@Component({
  selector: 'app-field-cell-renderer',
  templateUrl: './field-cell-renderer.component.html',
  styleUrls: ['./field-cell-renderer.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FieldCellRendererComponent implements ICellRendererAngularComp {
  params!: FieldCellRendererParams;

  agInit(params: FieldCellRendererParams): void {
    this.refresh(params);
  }

  refresh(params: FieldCellRendererParams): boolean {
    this.params = params;

    return true;
  }
}
