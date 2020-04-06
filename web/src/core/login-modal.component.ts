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

  async logIn(token: string) {
    const result = await this.apollo
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

    const resultData = result.data?.logIn ?? null;

    if (resultData !== null) {
      await this.authService.setAuth(resultData);
    }
  }
}
