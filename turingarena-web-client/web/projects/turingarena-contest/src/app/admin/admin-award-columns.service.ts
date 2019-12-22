import { Injectable } from '@angular/core';
import { ColDef, ColGroupDef } from 'ag-grid-community';

import { AwardFragment } from '../__generated__/AwardFragment';
import { AwardOutcomeFragment } from '../__generated__/AwardOutcomeFragment';
import { VariantService } from '../variant.service';

import { AdminProblemFragment } from './__generated__/AdminProblemFragment';
import { AdminQuery } from './__generated__/AdminQuery';
import { AdminUserFragment } from './__generated__/AdminUserFragment';

@Injectable({
  providedIn: 'root',
})
export class AdminAwardColumnsService {

  constructor(
    private readonly variantService: VariantService,
  ) { }

  getAwardColumns(data: AdminQuery): (ColDef | ColGroupDef)[] {
    const awardGetter = ({ scoreMap, user, problem, award }: {
      scoreMap: Map<string, AwardOutcomeFragment['value']>;
      user: AdminUserFragment;
      problem: AdminProblemFragment;
      award: AwardFragment;
    }) => ({
      score: 0,
      badge: false,
      ...scoreMap.get(`${user.id}/${problem.name}/${award.name}`),
    });

    return [
      {
        headerName: 'Awards',
        openByDefault: true,
        children: [
          ...data.problems.map((problem): ColGroupDef => ({
            headerName: this.variantService.selectTextVariant(problem.material.title),
            columnGroupShow: 'open',
            children: [
              ...problem.material.awards.map((award): ColDef => ({
                headerName: this.variantService.selectTextVariant(award.title),
                valueGetter: ({ node: { data: user }, context: { scoreMap } }) =>
                  awardGetter({ scoreMap, user, problem, award })[
                  award.content.__typename === 'ScoreAwardContent' ? 'score' : 'badge'
                  ],
                valueFormatter:
                  award.content.__typename === 'ScoreAwardContent'
                    ? ({ value }) => value
                    : ({ value }) => value ? 'yes' : 'no'
                ,
                columnGroupShow: 'open',
              })),
              {
                headerName: 'Score',
                valueGetter: ({ node: { data: user }, context: { scoreMap } }) => problem.material.awards
                  .map((award) => awardGetter({ scoreMap, user, problem, award }).score)
                  .reduce((a, b) => a + b, 0),
              },
            ],
          })),
          {
            headerName: 'Total score',
            valueGetter: ({ node: { data: user }, context: { scoreMap } }) => data.problems.map((problem) =>
              problem.material.awards
                .map((award) => awardGetter({ scoreMap, user, problem, award }).score)
                .reduce((a, b) => a + b, 0),
            ).reduce((a, b) => a + b, 0),
          },
        ],
      },
    ];
  }

}
