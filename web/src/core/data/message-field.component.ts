import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MessageFieldFragment } from '../../generated/graphql-types';
import { textFragment } from '../material/text.pipe';

@Component({
  selector: 'app-message-field',
  templateUrl: './message-field.component.html',
  styleUrls: ['./message-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MessageFieldComponent {
  @Input()
  data!: MessageFieldFragment;
}

export const timeUsageFieldFragment = gql`
  fragment MessageField on MessageField {
    message {
      ...Text
    }
  }

  ${textFragment}
`;
