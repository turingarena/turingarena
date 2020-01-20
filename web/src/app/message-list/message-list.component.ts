import { Component, Input } from '@angular/core';

import { MessageFragment } from '../fragments/__generated__/MessageFragment';

@Component({
  selector: 'app-message-list',
  templateUrl: './message-list.component.html',
  styleUrls: ['./message-list.component.scss'],
})
export class MessageListComponent {

  @Input()
  messages!: MessageFragment[];

  reverse<T>(list: T[]) {
    return list.slice().reverse();
  }

}
