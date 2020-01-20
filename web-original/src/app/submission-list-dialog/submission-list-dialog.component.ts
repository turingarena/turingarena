import { Component, Input } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ProblemFragment, SubmissionFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-submission-list-dialog',
  templateUrl: './submission-list-dialog.component.html',
  styleUrls: ['./submission-list-dialog.component.scss'],
})
export class SubmissionListDialogComponent {
  constructor(readonly modalService: NgbModal) {}

  @Input()
  modal!: NgbActiveModal;

  @Input()
  problem!: ProblemFragment;

  openSubmission!: SubmissionFragment;
}
