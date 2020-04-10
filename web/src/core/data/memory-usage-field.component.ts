import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MemoryUsageFieldFragment, MemoryUsageFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-memory-usage-field',
  templateUrl: './memory-usage-field.component.html',
  styleUrls: ['./memory-usage-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MemoryUsageFieldComponent {
  @Input()
  data!: MemoryUsageFieldFragment;

  // tslint:disable: no-magic-numbers
  displayMemoryUsage(memoryUsage: MemoryUsageFragment) {
    const { memoryUsageMaxRelevant } = this.data;

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
  }
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
    memoryUsagePrimaryWatermark {
      ...MemoryUsage
    }
  }
`;
