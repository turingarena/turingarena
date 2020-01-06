import { Component } from '@angular/core';
import { ICellRendererAngularComp } from 'ag-grid-angular';
import { ICellRendererParams } from 'ag-grid-community';

/**
 * An ag-grid cell renderer that uses an Angular template.
 */
@Component({
  selector: 'app-template-cell-renderer',
  template: '<ng-container *ngTemplateOutlet="params.template; context: params"></ng-container>',
})
export class TemplateCellRendererComponent implements ICellRendererAngularComp {
  params!: ICellRendererParams;

  agInit(params: ICellRendererParams): void {
    this.refresh(params);
  }

  refresh(params: ICellRendererParams): boolean {
    this.params = params;

    return true;
  }
}
