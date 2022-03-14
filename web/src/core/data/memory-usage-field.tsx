import { gql } from '@apollo/client';
import React from 'react';
import { MemoryUsageFieldFragment, MemoryUsageFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { displayByteSize } from './byte-size';

export function MemoryUsageField({ data }: FragmentProps<MemoryUsageFieldFragment>) {
  // tslint:disable: no-magic-numbers
  const displayMemoryUsage = (memoryUsage: MemoryUsageFragment) => {
    const { memoryUsageMaxRelevant } = data;
    const { bytes } = memoryUsage;

    return displayByteSize(bytes, memoryUsageMaxRelevant?.bytes);
  };

  return (
    <span className="memory-usage">
      {data.memoryUsage !== null && displayMemoryUsage(data.memoryUsage)}
      {data.memoryUsageWatermark !== null && <small> / {displayMemoryUsage(data.memoryUsageWatermark)}</small>}
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
