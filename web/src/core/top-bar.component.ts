import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { TopBarFragment } from '../generated/graphql-types';
import { AuthService } from '../util/auth.service';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class TopBarComponent {
  constructor(readonly modalService: NgbModal, readonly authService: AuthService) {}

  @Input()
  data!: TopBarFragment;

  messagesCount!: number;
  isAdmin!: boolean;

  logInInvalidToken!: boolean;

  async logOut() {
    await this.authService.removeAuth();
  }
}

export const topBarFragment = gql`
  fragment TopBar on MainView {
    title {
      ...Text
    }
    user {
      name
    }
  }

  ${textFragment}
`;
