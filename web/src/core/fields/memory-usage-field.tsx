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

    if (memoryUsageMaxRelevant.bytes > 100e6) {
      return `${mb.toFixed(1)} MB`;
    } else if (memoryUsageMaxRelevant.bytes > 10e6) {
      return `${mb.toFixed(2)} MB`;
    } else if (memoryUsageMaxRelevant.bytes > 1e6) {
      return `${kb.toFixed(0)} KB`;
    } else if (memoryUsageMaxRelevant.bytes > 100e3) {
      return `${kb.toFixed(1)} KB`;
    } else if (memoryUsageMaxRelevant.bytes > 10e3) {
      return `${kb.toFixed(2)} KB`;
    } else {
      return `${kb.toFixed(3)} KB`;
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
