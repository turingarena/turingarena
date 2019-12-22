import { Injectable } from '@angular/core';
import { ColDef, ColGroupDef, ValueGetterParams } from 'ag-grid-community';

import { AwardFragment } from '../__generated__/AwardFragment';
import { BadgeAwardValueFragment } from '../__generated__/BadgeAwardValueFragment';
import { MaterialFragment } from '../__generated__/MaterialFragment';
import { ScoreAwardValueFragment } from '../__generated__/ScoreAwardValueFragment';
import { getProblemScoreRange } from '../material';
import { getBadgeValence, getScoreValence } from '../score';
import { VariantService } from '../variant.service';

import { AdminQuery } from './__generated__/AdminQuery';

export interface AwardGetterParams {
  valueGetterParams: ValueGetterParams;
  problem: {
    name: string;
    material: MaterialFragment;
  };
  award: AwardFragment;
}

export interface AwardColumnsParams {
  data: AdminQuery;
  scoreGetter(params: AwardGetterParams): ScoreAwardValueFragment;
  badgeGetter(params: AwardGetterParams): BadgeAwardValueFragment;
}

const sortingOrder = ['desc', 'asc'];

@Injectable({
  providedIn: 'root',
})
export class AdminAwardColumnsService {

  constructor(
    private readonly variantService: VariantService,
  ) { }

  getAwardColumns({ data, badgeGetter, scoreGetter }: AwardColumnsParams): (ColDef | ColGroupDef)[] {
    return [
      {
        headerName: 'Awards',
        openByDefault: true,
        children: [
          ...data.problems.map((problem): ColGroupDef => ({
            headerName: problem.name,
            headerTooltip: this.variantService.selectTextVariant(problem.material.title),
            columnGroupShow: 'open',
            children: [
              ...problem.material.awards.map((award): ColDef => ({
                headerName: this.variantService.selectTextVariant(award.title),
                cellClass: ({ value }) => [
                  'grid-cell-valence',
                  award.content.__typename === 'ScoreAwardContent'
                    ? getScoreValence({ score: value, range: award.content.range })!.toLowerCase()
                    : getBadgeValence(value).toLowerCase(),
                ],
                valueGetter: (valueGetterParams) =>
                  award.content.__typename === 'ScoreAwardContent'
                    ? scoreGetter({ valueGetterParams, problem, award }).score
                    : badgeGetter({ valueGetterParams, problem, award }).badge,
                valueFormatter:
                  award.content.__typename === 'ScoreAwardContent'
                    ? ({ value }) => value
                    : ({ value }) => value ? 'yes' : 'no'
                ,
                flex: 0.6,
                columnGroupShow: 'open',
                sortingOrder,
              })),
              {
                headerName: 'Score',
                valueGetter: (valueGetterParams) => problem.material.awards
                  .map(
                    (award) => award.content.__typename === 'ScoreAwardContent'
                      ? scoreGetter({ valueGetterParams, problem, award }).score
                      : 0,
                  )
                  .reduce((a, b) => a + b, 0),
                cellClass: ({ value }) => [
                  'grid-cell-valence',
                  getScoreValence({ score: value, range: getProblemScoreRange(problem.material) })!.toLowerCase(),
                ],
                flex: 0.8,
                sortingOrder,
              },
            ],
          })),
          {
            headerName: 'Total score',
            valueGetter: (valueGetterParams) => data.problems.map((problem) =>
              problem.material.awards
                .map(
                  (award) => award.content.__typename === 'ScoreAwardContent'
                    ? scoreGetter({ valueGetterParams, problem, award }).score
                    : 0,
                )
                .reduce((a, b) => a + b, 0),
            ).reduce((a, b) => a + b, 0),
            cellClass: ({ value }) => [
              'grid-cell-valence',
              getScoreValence({
                score: value,
                range: {
                  max: data.problems.map((problem) => getProblemScoreRange(problem.material).max)
                    .reduce((a, b) => a + b, 0),
                },
              })!.toLowerCase(),
            ],
            flex: 1,
            sortingOrder,
          },
        ],
      },
    ];
  }

}
