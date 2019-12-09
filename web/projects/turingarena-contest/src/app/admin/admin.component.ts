import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

import { submissionAwardFragment } from '../awards';
import { problemMaterialFragment } from '../material';

import { AdminQuery } from './__generated__/AdminQuery';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent {

  constructor(
    private readonly apollo: Apollo,
    readonly route: ActivatedRoute,
  ) { }

  adminQuery = this.apollo.watchQuery<AdminQuery>({
    query: gql`
      query AdminQuery {
        serverTime
        problems {
          name
          material {
            ...MaterialFragment
          }
        }
        users {
          id
          displayName
        }
        awards {
          ...SubmissionAwardFragment
          submission {
            problemName
            userId
          }
        }
      }
      ${submissionAwardFragment}
      ${problemMaterialFragment}
    `,
    variables: {},
    pollInterval: 10000,
  });

  getScores(data: AdminQuery | undefined) {
    if (data === undefined) {
      return undefined;
    }

    const scoreMap = new Map(
      data.awards.map(({ awardName, submission: { problemName, userId }, value }) => [
        `${userId}/${problemName}/${awardName}`,
        value,
      ]),
    );

    return {
      getScore(userId: string, problemName: string, awardName: string) {
        const value = scoreMap.get(`${userId}/${problemName}/${awardName}`);

        return value !== undefined && value.__typename === 'ScoreAwardValue' ? value.score : 0;
      },
      getBadge(userId: string, problemName: string, awardName: string) {
        const value = scoreMap.get(`${userId}/${problemName}/${awardName}`);

        return value !== undefined && value.__typename === 'BadgeAwardValue' ? value.badge : false;
      },
    };
  }

}
