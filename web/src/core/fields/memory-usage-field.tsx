import { gql } from '@apollo/client';
import React from 'react';
import { MemoryUsageFieldFragment, MemoryUsageFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';

export function MemoryUsageField({ data }: FragmentProps<MemoryUsageFieldFragment>) {
  // tslint:disable: no-magic-numbers
  const displayMemoryUsage = (memoryUsage: MemoryUsageFragment) => {
    const { memoryUsageMaxRelevant } = data;

    const { bytes } = memoryUsage;
    const kb = bytes / 1024;
    const mb = kb / 1024;

    const truncate = memoryUsageMaxRelevant !== null;
    const scale = memoryUsageMaxRelevant ?? memoryUsage;

    if (scale.bytes > 100e6) {
      return `${truncate ? mb.toFixed(1) : mb} MB`;
    } else if (scale.bytes > 10e6) {
      return `${truncate ? mb.toFixed(2) : mb} MB`;
    } else if (scale.bytes > 1e6) {
      return `${truncate ? kb.toFixed(0) : mb} KB`;
    } else if (scale.bytes > 100e3) {
      return `${truncate ? kb.toFixed(1) : mb} KB`;
    } else if (scale.bytes > 10e3) {
      return `${truncate ? kb.toFixed(2) : mb} KB`;
    } else {
      return `${truncate ? kb.toFixed(3) : mb} KB`;
    }
  };

  return (
    <span className="memory-usage">
      {data.memoryUsage !== null && displayMemoryUsage(data.memoryUsage)}
      {data.memoryUsageWatermark !== null && (
        <small> / {displayMemoryUsage(data.memoryUsageWatermark)}</small>
      )}
    </span>
  );
}

export const memoryUsageFieldFragment = gql`
  fragment MemoryUsage on MemoryUsage {
    bytes
  }

  fragment MemoryUsageField on MemoryUsageField {
    memoryUsage {
      ...MemoryUsage
    }
    memoryUsageMaxRelevant {
      ...MemoryUsage
    }
    memoryUsageWatermark {
      ...MemoryUsage
    }
  }
`;
