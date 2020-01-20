import { Component, TemplateRef } from '@angular/core';
import { ICellRendererAngularComp } from 'ag-grid-angular';
import { ICellRendererParams } from 'ag-grid-community';

export type TemplateCellRendererParams = ICellRendererParams & { template: TemplateRef<unknown> };

/**
 * An ag-grid cell renderer that uses an Angular template.
 */
@Component({
  selector: 'app-template-cell-renderer',
  template: '<ng-container *ngTemplateOutlet="params.template; context: params"></ng-container>',
})
export class TemplateCellRendererComponent implements ICellRendererAngularComp {
  params!: TemplateCellRendererParams;

  agInit(params: TemplateCellRendererParams): void {
    this.refresh(params);
  }

  refresh(params: TemplateCellRendererParams): boolean {
    this.params = params;

    return true;
  }
}
