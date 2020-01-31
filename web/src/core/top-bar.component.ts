import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { TextFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class TopBarComponent {
  constructor(readonly modalService: NgbModal) {}

  @Input()
  title!: TextFragment;

  logInInvalidToken!: boolean;
  userDisplayName!: string | null;
  messagesCount!: number;
  isLoggedIn!: boolean;
  isAdmin!: boolean;

  logOut() {
    // TODO
  }
}
