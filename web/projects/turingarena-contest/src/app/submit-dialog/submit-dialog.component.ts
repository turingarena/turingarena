import { Component, Input } from '@angular/core';
import { AppComponent } from '../app.component';
import { ContestQuery_problems_material_submissionForm_fields as Field } from '../__generated__/ContestQuery';

@Component({
  selector: 'app-submit-dialog',
  templateUrl: './submit-dialog.component.html',
  styleUrls: ['./submit-dialog.component.scss']
})
export class SubmitDialogComponent {
  @Input()
  appComponent: AppComponent;

  @Input()
  problemName: string;

  private fields: Record<string, FieldState> = {};

  fieldState(field: Field) {
    const { id } = field;
    if (!this.fields[id]) {
      this.fields[id] = new FieldState(field);
    }
    return this.fields[id];
  }
}

class FieldState {
  file?: File;
  wantCustomTypes = false;

  constructor(private field: Field) { }

  isCompatible(type: Field['types'][number]) {
    return type.extensions.some(ext => this.file !== null && this.file.name.endsWith(ext));
  }

  get recommendedTypes() {
    return this.field.types.filter(t => this.isCompatible(t));
  }

  get notRecommendedTypes() {
    return this.field.types.filter(t => this.isCompatible(t));
  }
  get typeChoices() {
    const recommendedTypes = this.field.types.filter(t => this.isCompatible(t));
    const otherTypes = this.field.types.filter(t => !this.isCompatible(t));

    return this.wantCustomTypes || recommendedTypes.length === 0 ? {
      type: 'custom',
      allTypes: [...recommendedTypes, ...otherTypes],
    } : recommendedTypes.length === 1 ? {
      type: 'oneRecommended',
      recommendedType: recommendedTypes[0],
    } : {
          type: 'manyRecommended',
          recommendedTypes,
        };
  }
}

