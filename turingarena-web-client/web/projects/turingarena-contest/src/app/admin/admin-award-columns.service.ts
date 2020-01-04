import { Injectable } from '@angular/core';
import { ColDef, ColGroupDef, ValueFormatterParams, ValueGetterParams } from 'ag-grid-community';

import { Valence } from '../../../../../__generated__/globalTypes';
import { AwardFragment } from '../fragments/__generated__/AwardFragment';
import { BadgeAwardValueFragment } from '../fragments/__generated__/BadgeAwardValueFragment';
import { MaterialFragment } from '../fragments/__generated__/MaterialFragment';
import { ScoreAwardValueFragment } from '../fragments/__generated__/ScoreAwardValueFragment';
import { getBadgeValence, getScoreValence } from '../fragments/score';
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

const makeValenceClassRules = (valenceGetter: (params: ValueFormatterParams) => Valence) => {
  const rules: Record<string, (params: ValueFormatterParams) => boolean> = {};

  rules['grid-cell-valence'] = () => true;
  Object.keys(Valence).forEach((valence) => {
    rules[valence.toLowerCase()] = (params) => valenceGetter(params) === valence;
  });

  return rules;
};

@Injectable({
  providedIn: 'root',
})
export class AdminAwardColumnsService {

  constructor(
    private readonly variantService: VariantService,
  ) { }

  getAwardColumns({ data, badgeGetter, scoreGetter }: AwardColumnsParams): ColGroupDef[] {
    return [
      {
        headerName: 'Awards',
        openByDefault: true,
        groupId: `awards`,
        children: [
          ...data.problems.map((problem): ColGroupDef => ({
            headerName: problem.name,
            headerTooltip: this.variantService.selectTextVariant(problem.material.title),
            columnGroupShow: 'open',
            groupId: `awards/problem/${problem.name}`,
            children: [
              ...problem.material.awards.map((award): ColDef => ({
                colId: `awards/problem/${problem.name}/award/${award.name}`,
                headerName: this.variantService.selectTextVariant(award.title),
                type: 'numericColumn',
                cellClassRules: makeValenceClassRules(({ value }) => award.content.__typename === 'ScoreAwardContent'
                  ? getScoreValence({ score: value, range: award.content.range })!
                  : getBadgeValence(value),
                ),
                valueGetter: (valueGetterParams) =>
                  award.content.__typename === 'ScoreAwardContent'
                    ? scoreGetter({ valueGetterParams, problem, award }).score
                    : badgeGetter({ valueGetterParams, problem, award }).badge,
                valueFormatter:
                  award.content.__typename === 'ScoreAwardContent'
                    ? ({ value }) => value
                    : ({ value }) => value ? 'yes' : 'no'
                ,
                columnGroupShow: 'open',
                sortingOrder,
                flex: 1,
              })),
              {
                headerName: 'Score',
                colId: `awards/problem/${problem.name}/score`,
                type: 'numericColumn',
                valueGetter: (valueGetterParams) => problem.material.awards
                  .map(
                    (award) => award.content.__typename === 'ScoreAwardContent'
                      ? scoreGetter({ valueGetterParams, problem, award }).score
                      : 0,
                  )
                  .reduce((a, b) => a + b, 0),
                cellClassRules: makeValenceClassRules(({ value }) =>
                  getScoreValence({ score: value, range: problem.totalScoreRange })!),
                columnGroupShow: 'closed',
                sortingOrder,
                flex: 1,
              },
            ],
          })),
          {
            colId: `awards/total-score`,
            headerName: 'Total score',
            type: 'numericColumn',
            valueGetter: (valueGetterParams) => data.problems.map((problem) =>
              problem.material.awards
                .map(
                  (award) => award.content.__typename === 'ScoreAwardContent'
                    ? scoreGetter({ valueGetterParams, problem, award }).score
                    : 0,
                )
                .reduce((a, b) => a + b, 0),
            ).reduce((a, b) => a + b, 0),
            cellClassRules: makeValenceClassRules(({ value }) =>
              getScoreValence({
                score: value,
                range: {
                  max: data.problems.map((problem) => problem.totalScoreRange.max)
                    .reduce((a, b) => a + b, 0),
                },
              })!),
            flex: 1.2,
            sortingOrder,
          },
        ],
      },
    ];
  }

}
