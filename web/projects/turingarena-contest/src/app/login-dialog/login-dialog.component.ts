import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

import { AppComponent } from '../app.component';
import { LoginMutationService } from '../login-mutation.service';

@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  styleUrls: ['./login-dialog.component.scss'],
})
export class LoginDialogComponent implements OnInit {

  constructor(
    readonly activeModal: NgbActiveModal,
    readonly loginMutationService: LoginMutationService,
  ) { }

  @Input()
  appComponent!: AppComponent;

  ngOnInit() {
  }

  async submit(event: Event) {
    const formData = new FormData(event.target as HTMLFormElement);
    const { data } = await this.loginMutationService.mutate({
      token: formData.get('token') as string,
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
