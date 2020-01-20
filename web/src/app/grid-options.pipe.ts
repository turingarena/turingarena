import { Pipe, PipeTransform } from '@angular/core';
import { GridOptions } from 'ag-grid-community';

import { TemplateCellRendererComponent } from './template-cell-renderer.component';

/**
 * Provide default options for AgGrid.
 * A pipe (not, say, a service) because pipes are injected in templates.
 * FIXME: can we somehow use a directive, instead?
 */
@Pipe({
  name: 'gridOptions',
})
export class GridOptionsPipe implements PipeTransform {

  transform(value: GridOptions): GridOptions {
    return {
      frameworkComponents: {
        templateCellRenderer: TemplateCellRendererComponent,
      },
      ...value,
    };
  }

}
