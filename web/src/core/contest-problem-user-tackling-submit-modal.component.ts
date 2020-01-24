import { Component, Input, OnInit, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import {
  ContestProblemUserTacklingSubmitModalFragment,
  ContestProblemUserTacklingSubmitModalSubmissionFieldFragment,
  SubmissionFileInput,
  SubmitMutation,
  SubmitMutationVariables,
} from '../generated/graphql-types';
import { FileLoadService } from '../util/file-load.service';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-contest-problem-user-tackling-submit-modal',
  templateUrl: './contest-problem-user-tackling-submit-modal.component.html',
  styleUrls: ['./contest-problem-user-tackling-submit-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemUserTacklingSubmitModalComponent implements OnInit {
  constructor(private readonly apollo: Apollo, private readonly fileLoadService: FileLoadService) {}

  @Input()
  modal!: NgbActiveModal;

  @Input()
  data!: ContestProblemUserTacklingSubmitModalFragment;

  fieldStates: Record<
    string,
    {
      overrideDefaultType: boolean;
      file?: File;
    }
  > = {};

  submitting = false;

  ngOnInit() {
    for (const { name } of this.data.assignmentView.assignment.problem.submissionFields) {
      this.fieldStates[name] = {
        overrideDefaultType: false,
      };
    }
  }

  getTypingRule(file: File, field: ContestProblemUserTacklingSubmitModalSubmissionFieldFragment) {
    for (const rule of this.data.assignmentView.assignment.problem.submissionFileTypeRules) {
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
      this.data.assignmentView.assignment.problem.submissionFields.map(async field =>
        this.getFileForField(field, formData),
      ),
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
            contestName: this.data.assignmentView.assignment.contest.name,
            problemName: this.data.assignmentView.assignment.problem.name,
            username: this.data.user.username,
            files,
          },
        },
        refetchQueries: ['MainView'],
      })
      .toPromise();

    if (data === undefined || data === null || errors !== undefined) {
      throw new Error('error in submit');
    }

    this.modal.close();
  }

  private async getFileForField(
    field: ContestProblemUserTacklingSubmitModalSubmissionFieldFragment,
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

export const contestProblemUserTacklingSubmitModalFragment = gql`
  fragment ContestProblemUserTacklingSubmitModalSubmissionFileType on SubmissionFileType {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemUserTacklingSubmitModalSubmissionField on SubmissionField {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemUserTacklingSubmitModalSubmissionFileTypeRule on SubmissionFileTypeRule {
    fields {
      name
    }
    extensions
    defaultType {
      ...ContestProblemUserTacklingSubmitModalSubmissionFileType
    }
    recommendedTypes {
      ...ContestProblemUserTacklingSubmitModalSubmissionFileType
    }
    otherTypes {
      ...ContestProblemUserTacklingSubmitModalSubmissionFileType
    }
  }

  fragment ContestProblemUserTacklingSubmitModal on ContestProblemUserTackling {
    assignmentView {
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
            ...ContestProblemUserTacklingSubmitModalSubmissionField
          }
          submissionFileTypeRules {
            ...ContestProblemUserTacklingSubmitModalSubmissionFileTypeRule
          }
        }
      }
    }

    user {
      username
    }
  }

  ${textFragment}
`;
