import { Component, EventEmitter, Input, Output } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { FileInput } from '../../../../../__generated__/globalTypes';
import { FileLoadService } from '../file-load.service';
import { FieldFragment } from '../fragments/__generated__/FieldFragment';
import { FieldTypeFragment } from '../fragments/__generated__/FieldTypeFragment';
import { ProblemViewFragment } from '../fragments/__generated__/ProblemViewFragment';

import { SubmitMutation, SubmitMutationVariables } from './__generated__/SubmitMutation';

class FieldState {
  file?: File;
  moreTypes = false;

  constructor(private readonly field: FieldFragment) { }

  isCompatible(type: FieldTypeFragment) {
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
    private readonly fileLoadService: FileLoadService,
  ) { }

  @Input()
  problem!: ProblemViewFragment;

  @Input()
  userId!: string;

  @Input()
  modal!: NgbActiveModal;

  @Output()
  done = new EventEmitter();

  submitting = false;

  private readonly fields: Record<string, FieldState> = {};

  fieldState(field: FieldFragment) {
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
        mutation SubmitMutation($userId: String!, $problemName: String!, $files: [FileInput!]!) {
          submit(userId: $userId, problemName: $problemName, files: $files) {
            id
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

    this.done.emit({ id: data.submit.id });

    this.modal.close();
  }

  private async getFileForField(field: FieldFragment, formData: FormData): Promise<FileInput> {
    const file = formData.get(`${field.id}.file`) as File;

    return {
      fieldId: field.id,
      typeId: formData.get(`${field.id}.type`) as string,
      name: file.name,
      content: await this.fileLoadService.loadFileContent(file),
    };
  }

}
