import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemUserTacklingAsideFragment } from '../generated/graphql-types';
import { contestProblemUserTacklingSubmitModalFragment } from './contest-problem-user-tackling-submit-modal.component';

@Component({
  selector: 'app-contest-problem-user-tackling-aside',
  templateUrl: './contest-problem-user-tackling-aside.component.html',
  styleUrls: ['./contest-problem-user-tackling-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemUserTacklingAsideComponent {
  constructor(readonly modalService: NgbModal) {}

  @Input()
  data!: ContestProblemUserTacklingAsideFragment;
}

export const contestProblemUserTacklingAsideFragment = gql`
  fragment ContestProblemUserTacklingAside on ContestProblemUserTackling {
    canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }
    }

    ...ContestProblemUserTacklingSubmitModal
  }

  ${contestProblemUserTacklingSubmitModalFragment}
`;
