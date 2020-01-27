import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { FulfillmentFieldFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-fulfillment-field',
  templateUrl: './fulfillment-field.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class GradingBooleanComponent {
  @Input()
  data!: FulfillmentFieldFragment;
}

export const fulfillmentVariableFragment = gql`
  fragment FulfillmentField on FulfillmentField {
    fulfilled
    valence
  }
`;
