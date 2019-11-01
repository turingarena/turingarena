import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { LoginMutation, LoginMutationVariables } from '../__generated__/LoginMutation';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  styleUrls: ['./login-dialog.component.scss'],
})
export class LoginDialogComponent {

  constructor(
    private readonly authService: AuthService,
    readonly activeModal: NgbActiveModal,
    readonly apollo: Apollo,
  ) { }

  async submit(event: Event) {
    const formData = new FormData(event.target as HTMLFormElement);
    const { data } = await this.apollo.mutate<LoginMutation, LoginMutationVariables>({
      mutation: gql`
        mutation LoginMutation($token: String!) {
          auth(token: $token) {
            token
            userId
          }
        }
      `,
      variables: {
        token: formData.get('token') as string,
      },
    }).toPromise();

    if (data === null || data === undefined) { throw Error('error during login'); }

    if (data.auth === null) {
      // FIXME
      alert('Login failed');
    } else {
      const { token, userId } = data.auth;

      await this.authService.setAuth({ token, userId });

      this.activeModal.close();
    }
  }

}
