import { gql } from '@apollo/client';
import { Duration } from 'luxon';
import React from 'react';
import { TimeUsageFieldFragment, TimeUsageFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';

export function TimeUsageField({ data }: FragmentProps<TimeUsageFieldFragment>) {
  const displayTimeUsage = (timeUsage: TimeUsageFragment) => {
    const { timeUsageMaxRelevant } = data;

    const truncate = timeUsageMaxRelevant !== null;
    const scale = timeUsageMaxRelevant ?? timeUsage;

    const extraPrecision = 3;
    const fractionDigits = Math.max(Math.round(-Math.log10(scale.seconds) + extraPrecision), 0);
    const millisPrecision = 3;

    const duration = Duration.fromObject({ seconds: timeUsage.seconds });
    if (fractionDigits > millisPrecision) {
      const ms = duration.as('milliseconds');
      return `${truncate ? ms.toFixed(fractionDigits - millisPrecision) : ms} ms`;
    } else {
      const s = duration.as('seconds');
      return `${truncate ? s.toFixed(fractionDigits) : s} s`;
    }
  };

  return (
    <span className="time-usage">
      {data.timeUsage !== null && displayTimeUsage(data.timeUsage)}
      {data.timeUsageWatermark !== null && <small> / {displayTimeUsage(data.timeUsageWatermark)}</small>}
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
    timeUsageWatermark {
      ...TimeUsage
    }
  }
`;
