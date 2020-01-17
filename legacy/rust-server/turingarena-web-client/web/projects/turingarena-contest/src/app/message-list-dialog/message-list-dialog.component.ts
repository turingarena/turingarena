import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo } from 'apollo-angular';
import { FetchResult } from 'apollo-link';
import gql from 'graphql-tag';

import { ContestQuery } from '../contest-view/__generated__/ContestQuery';

import { SendMessageMutation, SendMessageMutationVariables } from './__generated__/SendMessageMutation';

@Component({
  selector: 'app-message-list-dialog',
  templateUrl: './message-list-dialog.component.html',
  styleUrls: ['./message-list-dialog.component.scss'],
})
export class MessageListDialogComponent {

  constructor(
    private readonly apollo: Apollo,
  ) { }

  @Input()
  data!: ContestQuery[];

  @Input()
  userId?: string;

  @Input()
  modal!: NgbActiveModal;

  sendMutationResult?: Promise<FetchResult<SendMessageMutation>>;

  async send(event: Event) {
    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);

    form.reset();

    console.log(event);

    this.sendMutationResult = this.apollo.mutate<SendMessageMutation, SendMessageMutationVariables>({
      mutation: gql`
        mutation SendMessageMutation($userId: String!, $text: String!) {
          sendMessage(userId: $userId, text: $text) {
            ok
          }
        }
      `,
      variables: {
        userId: this.userId!,
        text: formData.get('text') as string,
      },
      refetchQueries: ['ContestQuery'],
      awaitRefetchQueries: true,
    }).toPromise();
  }
}
