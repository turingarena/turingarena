import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { FieldFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-field',
  templateUrl: './field.component.html',
  styleUrls: ['./field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FieldComponent {
  @Input()
  data!: FieldFragment;
}

export const fieldFragment = gql`
  fragment Field on Field {
    ... on FulfillmentField {
      ...FulfillmentField
    }
    ... on ScoreField {
      ...ScoreField
    }
    ... on IndexHeaderField {
      index
    }
    ... on TitleHeaderField {
      title {
        ...Text
      }
    }
    ... on MessageField {
      message {
        ...Text
      }
    }
    ... on TimeUsageField {
      timeUsage {
        seconds
      }
    }
    ... on MemoryUsageField {
      memoryUsage {
        bytes
      }
    }
  }
`;
