import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { LoginMutation, LoginMutationVariables } from '../__generated__/LoginMutation';
import { AppComponent } from '../app.component';

@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  styleUrls: ['./login-dialog.component.scss'],
})
export class LoginDialogComponent implements OnInit {

  constructor(
    readonly activeModal: NgbActiveModal,
    readonly apollo: Apollo,
  ) { }

  @Input()
  appComponent!: AppComponent;

  ngOnInit() {
  }

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
      this.appComponent.setAuth({ token, userId });

      this.activeModal.close();
    }
  }

}
