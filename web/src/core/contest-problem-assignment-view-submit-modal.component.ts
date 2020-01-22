import { Component, Input, OnInit, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import {
  ContestProblemAssignmentViewSubmitModalFragment,
  ContestProblemAssignmentViewSubmitModalSubmissionFieldFragment,
  SubmissionFileInput,
  SubmitMutation,
  SubmitMutationVariables,
} from '../generated/graphql-types';
import { FileLoadService } from '../util/file-load.service';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-assignment-view-submit-modal',
  templateUrl: './contest-problem-assignment-view-submit-modal.component.html',
  styleUrls: ['./contest-problem-assignment-view-submit-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentViewSubmitModalComponent implements OnInit {
  constructor(private readonly apollo: Apollo, private readonly fileLoadService: FileLoadService) {}

  @Input()
  modal!: NgbActiveModal;

  @Input()
  data!: ContestProblemAssignmentViewSubmitModalFragment;

  fieldStates: Record<
    string,
    {
      overrideDefaultType: boolean;
      file?: File;
    }
  > = {};

  submitting = false;

  ngOnInit() {
    for (const { name } of this.data.assignment.problem.submissionFields) {
      this.fieldStates[name] = {
        overrideDefaultType: false,
      };
    }
  }

  getTypingRule(file: File, field: ContestProblemAssignmentViewSubmitModalSubmissionFieldFragment) {
    for (const rule of this.data.assignment.problem.submissionFileTypeRules) {
      const { fields = null, extensions = null } = rule;
      if (fields !== null && fields.find(f => f.name === field.name) === undefined) continue;
      if (extensions !== null && extensions.find(e => file.name.endsWith(e)) === undefined) continue;

      return rule;
    }
    throw new Error(`No file type rule matches the given field and file. The rules must include a catch-all rule.`);
  }

  async submit(event: Event) {
    const formData = new FormData(event.target as HTMLFormElement);

    if (this.submitting) return;
    this.submitting = true;

    const files = await Promise.all(
      this.data.assignment.problem.submissionFields.map(async field => this.getFileForField(field, formData)),
    );

    const { data, errors } = await this.apollo
      .mutate<SubmitMutation, SubmitMutationVariables>({
        mutation: gql`
          mutation Submit($submission: SubmissionInput!) {
            submit(submission: $submission)
          }
        `,
        variables: {
          submission: {
            contestName: this.data.assignment.contest.name,
            problemName: this.data.assignment.problem.name,
            // FIXME: canSubmit can be replaced by some structure containing a non-null user.
            username: this.data.user!.username,
            files,
          },
        },
        refetchQueries: ['ContestQuery'],
      })
      .toPromise();

    if (data === undefined || data === null || errors !== undefined) {
      throw new Error('error in submit');
    }

    this.modal.close();
  }

  private async getFileForField(
    field: ContestProblemAssignmentViewSubmitModalSubmissionFieldFragment,
    formData: FormData,
  ): Promise<SubmissionFileInput> {
    const file = formData.get(`${field.name}.file`) as File;

    return {
      fieldName: field.name,
      fileTypeName: formData.get(`${field.name}.type`) as string,
      fileName: file.name,
      content: await this.fileLoadService.loadFileContent(file),
    };
  }
}

export const contestProblemAssignmentViewSubmitModalFragment = gql`
  fragment ContestProblemAssignmentViewSubmitModalSubmissionFileType on SubmissionFileType {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemAssignmentViewSubmitModalSubmissionField on SubmissionField {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemAssignmentViewSubmitModalSubmissionFileTypeRule on SubmissionFileTypeRule {
    fields {
      name
    }
    extensions
    defaultType {
      ...ContestProblemAssignmentViewSubmitModalSubmissionFileType
    }
    recommendedTypes {
      ...ContestProblemAssignmentViewSubmitModalSubmissionFileType
    }
    otherTypes {
      ...ContestProblemAssignmentViewSubmitModalSubmissionFileType
    }
  }

  fragment ContestProblemAssignmentViewSubmitModal on ContestProblemAssignmentView {
    assignment {
      contest {
        name
      }
      problem {
        name
        title {
          ...Text
        }
        submissionFields {
          ...ContestProblemAssignmentViewSubmitModalSubmissionField
        }
        submissionFileTypeRules {
          ...ContestProblemAssignmentViewSubmitModalSubmissionFileTypeRule
        }
      }
    }

    user {
      username
    }
  }

  ${textFragment}
`;
