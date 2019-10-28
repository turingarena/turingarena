import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FileInput } from '../../../../../__generated__/globalTypes';
import { SubmitMutationService } from '../submit-mutation.service';
import {
  ContestQuery_contestView_problems_material_submissionForm_fields as Field,
  ContestQuery_contestView_problems as Problem,
} from '../__generated__/ContestQuery';

@Component({
  selector: 'app-submit-dialog',
  templateUrl: './submit-dialog.component.html',
  styleUrls: ['./submit-dialog.component.scss']
})
export class SubmitDialogComponent {
  constructor(
    private submitMutation: SubmitMutationService,
  ) { }

  @Input()
  problem: Problem;

  @Input()
  userId: string;

  @Input()
  modal: NgbActiveModal;

  @Output()
  done = new EventEmitter();

  submitting = false;

  private fields: Record<string, FieldState> = {};

  fieldState(field: Field) {
    const { id } = field;
    if (!this.fields[id]) {
      this.fields[id] = new FieldState(field);
    }
    return this.fields[id];
  }

  async submit(event: Event) {
    const formData = new FormData(event.target as HTMLFormElement);

    if (this.submitting) {
      return;
    }
    this.submitting = true;

    const files = await Promise.all(
      this.problem.material.submissionForm.fields.map(async (field) => this.getFileForField(field, formData))
    );

    console.log(files);

    const { data, errors } = await this.submitMutation.mutate({
      problemName: this.problem.name,
      userId: this.userId,
      files,
    }).toPromise();

    if (!data || errors) {
      throw new Error('error in submit');
    }

    this.done.emit({ id: data.contestView.problem.submit.id });

    this.modal.close();
  }

  private async getFileForField(field: Field, formData: FormData): Promise<FileInput> {
    const file = formData.get(`${field.id}.file`) as File;
    return {
      fieldId: field.id,
      typeId: formData.get(`${field.id}.type`) as string,
      name: file.name,
      contentBase64: await this.toBase64(file),
    };
  }

  private toBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (ev) => {
        const url = (ev.target as any).result as string;
        resolve(url.substring(url.indexOf(',') + 1));
      };

      reader.onerror = (ev) => {
        reject(ev);
      };

      reader.readAsDataURL(file);
    });
  }

}

class FieldState {
  file?: File;
  moreTypes = false;

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

    return this.moreTypes || recommendedTypes.length === 0 ? {
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

