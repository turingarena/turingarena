import { Component, Input } from '@angular/core';
import { AppComponent } from '../app.component';
import { ContestQuery_problems_material_submissionForm_fields as Field } from '../__generated__/ContestQuery';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { SubmitMutationService } from '../submit-mutation.service';
import { FileInput } from '../../../../../__generated__/globalTypes';
import { SubmissionDialogComponent } from '../submission-dialog/submission-dialog.component';
import { SubmissionQueryService } from '../submission-query.service';

@Component({
  selector: 'app-submit-dialog',
  templateUrl: './submit-dialog.component.html',
  styleUrls: ['./submit-dialog.component.scss']
})
export class SubmitDialogComponent {
  constructor(
    private activeModal: NgbActiveModal,
    private modal: NgbModal,
    private submitMutation: SubmitMutationService,
    private submissionQueryService: SubmissionQueryService,
  ) { }

  @Input()
  appComponent: AppComponent;

  @Input()
  problemName: string;

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

    const contest = this.appComponent.contestQuery.getLastResult().data;
    const problem = contest.problems.find((p) => p.name === this.problemName);
    const files = await Promise.all(
      problem.material.submissionForm.fields.map(async (field) => this.getFileForField(field, formData))
    );

    console.log(files);

    const { data, errors } = await this.submitMutation.mutate({
      problemName: this.problemName,
      userId: 'test', // FIXME
      files,
    }).toPromise();

    if (!data || errors) {
      throw new Error('error in submit');
    }

    this.activeModal.close();

    const modalRef = this.modal.open(SubmissionDialogComponent);
    const modal = modalRef.componentInstance as SubmissionDialogComponent;

    modal.setSubmissionQueryRef(this.submissionQueryService.watch({
      submissionId: data.submit.id,
    }, {
        pollInterval: 1000,
      }));
    modal.appComponent = this.appComponent;
    modal.problemName = this.problemName;
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

