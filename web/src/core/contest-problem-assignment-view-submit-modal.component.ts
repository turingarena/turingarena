import { Component, Input, OnInit, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import {
  ContestProblemAssignmentViewSubmitModalFragment,
  ContestProblemAssignmentViewSubmitModalSubmissionFieldFragment,
} from '../generated/graphql-types';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-assignment-view-submit-modal',
  templateUrl: './contest-problem-assignment-view-submit-modal.component.html',
  styleUrls: ['./contest-problem-assignment-view-submit-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentViewSubmitModalComponent implements OnInit {
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
  }

  ${textFragment}
`;
