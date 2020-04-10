import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { TimeUsageFieldFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-time-usage-field',
  templateUrl: './time-usage-field.component.html',
  styleUrls: ['./time-usage-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class TimeUsageFieldComponent {
  @Input()
  data!: TimeUsageFieldFragment;
}

export const timeUsageFieldFragment = gql`
  fragment TimeUsage on TimeUsage {
    seconds
  }

  fragment TimeUsageField on TimeUsageField {
    timeUsage {
      ...TimeUsage
    }
    timeUsageMaxRelevant {
      ...TimeUsage
    }
    timeUsagePrimaryWatermark {
      ...TimeUsage
    }
  }
`;
