import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MemoryUsageFieldFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-memory-usage-field',
  templateUrl: './memory-usage-field.component.html',
  styleUrls: ['./memory-usage-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MemoryUsageFieldComponent {
  @Input()
  data!: MemoryUsageFieldFragment;
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
