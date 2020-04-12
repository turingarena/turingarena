import { gql } from '@apollo/client';
import { Duration } from 'luxon';
import React from 'react';
import { TimeUsageFieldFragment, TimeUsageFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';

export function TimeUsageField({ data }: FragmentProps<TimeUsageFieldFragment>) {
  const displayTimeUsage = (timeUsage: TimeUsageFragment) => {
    const { timeUsageMaxRelevant } = data;

    const extraPrecision = 3;
    const fractionDigits = Math.max(Math.round(-Math.log10(timeUsageMaxRelevant.seconds) + extraPrecision), 0);
    const millisPrecision = 3;

    const duration = Duration.fromObject({ seconds: timeUsage.seconds });
    if (fractionDigits > millisPrecision) {
      return `${duration.as('milliseconds').toFixed(fractionDigits - millisPrecision)} ms`;
    } else {
      return `${duration.as('seconds').toFixed(fractionDigits)} s`;
    }
  };

  return (
    <span className="time-usage">
      {data.timeUsage !== null && displayTimeUsage(data.timeUsage)}
      {data.timeUsagePrimaryWatermark !== null && <small> / {displayTimeUsage(data.timeUsagePrimaryWatermark)}</small>}
    </span>
  );
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
