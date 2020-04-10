import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { LoginMutation, LoginMutationVariables } from '../generated/graphql-types';
import { AuthService } from '../util/auth.service';

@Component({
  selector: 'app-login-modal',
  templateUrl: './login-modal.component.html',
  styleUrls: ['./login-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class LoginModalComponent {
  constructor(private readonly apollo: Apollo, private readonly authService: AuthService) {}

  @Input()
  modal!: NgbActiveModal;

  invalidToken = false;

  async logIn(token: string) {
    const { data } = await this.apollo
      .mutate<LoginMutation, LoginMutationVariables>({
        mutation: gql`
          mutation Login($token: String!) {
            logIn(token: $token) {
              user {
                name
                username
              }
              token
            }
          }
        `,
        variables: {
          token,
        },
        fetchPolicy: 'no-cache',
      })
      .toPromise();

    if (data === null || data === undefined) {
      throw Error('error during login');
    }

    if (data.logIn === null) {
      this.invalidToken = true;

      return;
    }

    await this.authService.setAuth(data.logIn);

    this.modal.close();
  }
}
