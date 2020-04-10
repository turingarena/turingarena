import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { Duration } from 'luxon';
import { TimeUsageFieldFragment, TimeUsageFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-time-usage-field',
  templateUrl: './time-usage-field.component.html',
  styleUrls: ['./time-usage-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class TimeUsageFieldComponent {
  @Input()
  data!: TimeUsageFieldFragment;

  displayTimeUsage(timeUsage: TimeUsageFragment) {
    const { timeUsageMaxRelevant } = this.data;

    const extraPrecision = 3;
    const fractionDigits = Math.max(Math.round(-Math.log10(timeUsageMaxRelevant.seconds) + extraPrecision), 0);
    const millisPrecision = 3;

    const duration = Duration.fromObject({ seconds: timeUsage.seconds });
    if (fractionDigits > millisPrecision) {
      return `${duration.as('milliseconds').toFixed(fractionDigits - millisPrecision)} ms`;
    } else {
      return `${duration.as('seconds').toFixed(fractionDigits)} s`;
    }
  }
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
