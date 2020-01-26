import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { FulfillmentVariableFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-fulfillment-variable',
  templateUrl: './fulfillment-variable.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class GradingBooleanComponent {
  @Input()
  data!: FulfillmentVariableFragment;
}

export const booleanGradeVariableFragment = gql`
  fragment FulfillmentVariable on FulfillmentVariable {
    value {
      fulfilled
    }
  }
`;
