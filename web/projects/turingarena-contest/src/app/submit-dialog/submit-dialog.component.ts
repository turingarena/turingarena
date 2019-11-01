import { Component, EventEmitter, Input, Output } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { FileInput } from '../../../../../__generated__/globalTypes';
import {
  ContestQuery_contestView_problems as Problem,
  ContestQuery_contestView_problems_material_submissionForm_fields as Field,
} from '../__generated__/ContestQuery';
import { SubmitMutation, SubmitMutationVariables } from '../__generated__/SubmitMutation';

class FieldState {
  file?: File;
  moreTypes = false;

  constructor(private readonly field: Field) { }

  isCompatible(type: Field['types'][number]) {
    return type.extensions.some((ext) => this.file !== undefined && this.file.name.endsWith(ext));
  }

  get recommendedTypes() {
    return this.field.types.filter((t) => this.isCompatible(t));
  }

  get notRecommendedTypes() {
    return this.field.types.filter((t) => this.isCompatible(t));
  }

  get typeChoices() {
    const recommendedTypes = this.field.types.filter((t) => this.isCompatible(t));
    const otherTypes = this.field.types.filter((t) => !this.isCompatible(t));

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

@Component({
  selector: 'app-submit-dialog',
  templateUrl: './submit-dialog.component.html',
  styleUrls: ['./submit-dialog.component.scss'],
})
export class SubmitDialogComponent {
  constructor(
    private readonly apollo: Apollo,
  ) { }

  @Input()
  problem!: Problem;

  @Input()
  userId!: string;

  @Input()
  modal!: NgbActiveModal;

  @Output()
  done = new EventEmitter();

  submitting = false;

  private readonly fields: Record<string, FieldState> = {};

  fieldState(field: Field) {
    const { id } = field;
    if (!(id in this.fields)) {
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
      this.problem.material.submissionForm.fields.map(async (field) => this.getFileForField(field, formData)),
    );

    console.log(files);

    const { data, errors } = await this.apollo.mutate<SubmitMutation, SubmitMutationVariables>({
      mutation: gql`
        mutation SubmitMutation($userId: UserId!, $problemName: ProblemName!, $files: [FileInput!]!) {
          contestView(userId: $userId) {
            problem(name: $problemName) {
              tackling {
                submit(files: $files) {
                  id
                }
              }
            }
          }
        }
      `,
      variables: {
        problemName: this.problem.name,
        userId: this.userId,
        files,
      },
    })
      .toPromise();

    if (data === undefined || data === null || errors !== undefined) {
      throw new Error('error in submit');
    }

    this.done.emit({ id: data.contestView.problem.tackling!.submit.id });

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

  private async toBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (ev) => {
        const url = (ev.target as unknown as { result: string }).result;
        resolve(url.substring(url.indexOf(',') + 1));
      };

      reader.onerror = (ev) => {
        reject(ev);
      };

      reader.readAsDataURL(file);
    });
  }

}
