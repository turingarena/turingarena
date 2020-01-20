import { Component, Input, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ColDef, ValueGetterParams } from 'ag-grid-community';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { Duration } from 'luxon';
import {
  AwardFragment,
  CellFragment,
  ColFragment,
  MemoryUsageValueFragment,
  ProblemFragment,
  ScoreRangeFragment,
  ScoreValueFragment,
  SubmissionQuery,
  SubmissionQueryVariables,
  TableSectionFragment,
  TextValueFragment,
  TimeUsageCellContentFragment,
  TimeUsageValueFragment,
  Valence,
  ValenceValueFragment,
  ValueFragment,
} from '../../generated/graphql-types';
import { evaluationEventFragment, evaluationFragment } from '../fragments/evaluation';
import { submissionFragment } from '../fragments/submission';
import { VariantService } from '../variant.service';

@Component({
  selector: 'app-submission-dialog',
  templateUrl: './submission-dialog.component.html',
  styleUrls: ['./submission-dialog.component.scss'],
})
export class SubmissionDialogComponent implements OnInit {
  constructor(private readonly apollo: Apollo, private readonly variantService: VariantService) {}

  faSpinner = faSpinner;

  @Input()
  submissionId!: string;

  @Input()
  problem!: ProblemFragment;

  @Input()
  modal!: NgbActiveModal;

  @ViewChild('scoreCell', { static: false })
  scoreCell!: TemplateRef<unknown>;
  @ViewChild('timeUsageCell', { static: false })
  timeUsageCell!: TemplateRef<unknown>;
  @ViewChild('memoryUsageCell', { static: false })
  memoryUsageCell!: TemplateRef<unknown>;
  @ViewChild('messageCell', { static: false })
  messageCell!: TemplateRef<unknown>;

  submissionQueryRef!: QueryRef<SubmissionQuery, SubmissionQueryVariables>;

  ngOnInit() {
    const { submissionId } = this;
    this.submissionQueryRef = this.apollo.watchQuery({
      query: gql`
        query SubmissionQuery($submissionId: String!) {
          submission(submissionId: $submissionId) {
            ...SubmissionFragment
            evaluation {
              ...EvaluationFragment
              events {
                ...EventFragment
              }
            }
          }
        }
        ${submissionFragment}
        ${evaluationFragment}
        ${evaluationEventFragment}
      `,
      variables: { submissionId },
      pollInterval: 1000,
    });
  }

  getEvaluationRecord(query: SubmissionQuery) {
    const record: Record<string, ValueFragment> = {};
    for (const event of query.submission.evaluation.events) {
      if (event.__typename === 'ValueEvent') {
        const { key, value } = event;
        record[key] = value;
      }
    }

    return record;
  }

  displayTimeUsageSeconds(seconds: number, content: TimeUsageCellContentFragment) {
    const maxRelevant = content.timeUsageMaxRelevant;
    const extraPrecision = 3;
    const fractionDigits = Math.max(Math.round(-Math.log10(maxRelevant.seconds) + extraPrecision), 0);

    const millisPrecision = 3;

    const duration = Duration.fromObject({ seconds });
    if (fractionDigits > millisPrecision) {
      return `${duration.as('milliseconds').toFixed(fractionDigits - millisPrecision)} ms`;
    } else {
      return `${duration.as('seconds').toFixed(fractionDigits)} s`;
    }
  }

  getScoreValence(value: ScoreValueFragment | undefined, range: ScoreRangeFragment): Valence | undefined {
    if (value === undefined) {
      return undefined;
    }
    const { score } = value;
    if (score <= 0) {
      return Valence.FAILURE;
    }
    if (score < range.max) {
      return Valence.PARTIAL;
    }

    return Valence.SUCCESS;
  }

  // tslint:disable-next-line: cyclomatic-complexity
  private getCellData(
    col: ColFragment,
    cell: CellFragment,
    { context: { problem, record } }: ValueGetterParams,
  ): {
    value?: unknown;
    cellTemplateRef?: TemplateRef<unknown>;
    cellTemplateParams?: unknown;
  } {
    const unexpected = (): never => {
      throw new Error(`unexpected combination: ${col.content.__typename} / ${cell.content.__typename}`);
    };
    const get = <T>(key: string | null, mapper: (x: T) => unknown = x => x): unknown => {
      const rawValue = key !== null && key in record ? record[key] : undefined;
      if (rawValue === undefined) {
        return undefined;
      }

      return mapper(rawValue as T);
    };

    const content = cell.content;
    if (content.__typename === 'NotAvailableCellContent') {
      return {};
    }
    switch (col.content.__typename) {
      case 'RowNumberColContent':
        switch (content.__typename) {
          case 'RowNumberCellContent':
            return { value: content.number };
          default:
            throw unexpected();
        }
      case 'RowTitleColContent':
        switch (content.__typename) {
          case 'RowTitleCellContent':
            return { value: content.title };
          default:
            throw unexpected();
        }
      case 'MessageColContent':
        switch (content.__typename) {
          case 'MessageCellContent':
            return {
              value: get(content.key, (value: TextValueFragment) => this.variantService.selectTextVariant(value.text)),
              cellTemplateRef: this.messageCell,
              cellTemplateParams: {
                valence: get(content.valenceKey, (value: ValenceValueFragment) => value.valence),
              },
            };
          default:
            throw unexpected();
        }
      case 'ScoreColContent':
        switch (content.__typename) {
          case 'ScoreCellContent':
            return {
              value: get(content.key, (value: ScoreValueFragment) => value.score),
              cellTemplateRef: this.scoreCell,
              cellTemplateParams: {
                valence: get(content.key, (value: ScoreValueFragment) => this.getScoreValence(value, content.range)),
              },
            };
          default:
            throw unexpected();
        }
      case 'MemoryUsageColContent':
        switch (content.__typename) {
          case 'MemoryUsageCellContent':
            return {
              value: get(content.key, (value: MemoryUsageValueFragment) => value.memoryUsage.bytes),
              cellTemplateRef: this.memoryUsageCell,
              cellTemplateParams: {
                valence: get(content.valenceKey, (value: ValenceValueFragment) => value.valence),
              },
            };
          default:
            throw unexpected();
        }
      case 'TimeUsageColContent':
        switch (content.__typename) {
          case 'TimeUsageCellContent':
            return {
              value:
                content.key in record ? (record[content.key] as TimeUsageValueFragment).timeUsage.seconds : undefined,
              cellTemplateRef: this.timeUsageCell,
              cellTemplateParams: {
                valence: get(content.valenceKey, (value: ValenceValueFragment) => value.valence),
              },
            };
          default:
            throw unexpected();
        }
      case 'AwardReferenceColContent':
        switch (content.__typename) {
          case 'AwardReferenceCellContent':
            return {
              value: problem.material.awards.find((award: AwardFragment) => award.name === content.awardName),
            };
          default:
            throw unexpected();
        }
      default:
        throw unexpected();
    }
  }

  private getColDef(col: ColFragment): ColDef {
    const inverseSortingOrder = ['desc', 'asc', null] as string[]; // Incorrectly typed in ag-grid

    switch (col.content.__typename) {
      case 'ScoreColContent':
        return {
          cellClass: ['grid-cell-score', 'grid-cell-valence'],
          sortable: true,
          filter: 'agNumberColumnFilter',
        };
      case 'MessageColContent':
        return {
          flex: 2,
          cellClass: ['grid-cell-message', 'grid-cell-valence'],
        };
      case 'MemoryUsageColContent':
        return {
          cellClass: ['grid-cell-memory-usage', 'grid-cell-valence'],
          sortable: true,
          sortingOrder: inverseSortingOrder,
        };
      case 'TimeUsageColContent':
        return {
          cellClass: ['grid-cell-time-usage', 'grid-cell-valence'],
          sortable: true,
          sortingOrder: inverseSortingOrder,
        };
      case 'AwardReferenceColContent':
        return {
          valueFormatter: ({ value }) => this.variantService.selectTextVariant((value as AwardFragment).material.title),
        };
      default:
        return {};
    }
  }

  getColumnDefs = (data: unknown, section: TableSectionFragment) =>
    section.cols.map(
      (col, i): ColDef => ({
        colId: `${i}`,
        flex: 1,
        resizable: true,
        headerName: this.variantService.selectTextVariant(col.title),
        valueGetter: params => this.getCellData(col, params.data.cells[i], params).value,
        cellRendererSelector: params => {
          const cell = params.data.cells[i];
          const { cellTemplateRef, cellTemplateParams } = this.getCellData(col, cell, params);

          if (cellTemplateRef !== undefined) {
            return {
              component: 'templateCellRenderer',
              params: { template: cellTemplateRef, cell, ...cellTemplateParams },
            };
          }

          return {};
        },
        ...this.getColDef(col),
      }),
    );
}
