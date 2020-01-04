import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {
  faAward,
  faCheck,
  faChevronLeft,
  faChevronRight,
  faFile,
  faFileAlt,
  faFileArchive,
  faFilePdf,
  faHistory,
  faHome,
  faHourglassHalf,
  faList,
  faPaperPlane,
  faSignInAlt,
  faSignOutAlt,
  faSpinner,
} from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { DateTime, Duration } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { Auth, AuthService } from '../auth.service';
import { contestMaterialFragment } from '../fragments/contest';
import { problemFragment, problemViewFragment } from '../fragments/problem';
import { getScoreTier, scoreRangeFragment } from '../fragments/score';

import { ContestQuery, ContestQueryVariables } from './__generated__/ContestQuery';
import { LoginMutation, LoginMutationVariables } from './__generated__/LoginMutation';

const pollInterval = 5000;

@Component({
  selector: 'app-contest-view',
  templateUrl: './contest-view.component.html',
  styleUrls: ['./contest-view.component.scss'],
})
export class ContestViewComponent implements OnInit {

  constructor(
    private readonly authService: AuthService,
    private readonly apollo: Apollo,
    readonly route: ActivatedRoute,
    readonly modalService: NgbModal,
  ) { }

  get userId() {
    const auth = this.authService.getAuth();

    return auth !== undefined ? auth.userId : undefined;
  }

  faHome = faHome;
  faPaperPlane = faPaperPlane;
  faCheck = faCheck;
  faSignInAlt = faSignInAlt;
  faSignOutAlt = faSignOutAlt;
  faList = faList;
  faFilePdf = faFilePdf;
  faHistory = faHistory;
  faSpinner = faSpinner;
  faChevronLeft = faChevronLeft;
  faChevronRight = faChevronRight;
  faHourglassHalf = faHourglassHalf;
  faAward = faAward;

  mimeTypeIcons = {
    'application/pdf': faFilePdf,
    'text/plain': faFileAlt,
    'application/gzip': faFileArchive,
    'application/zip': faFileArchive,
  };
  faFile = faFile;

  focusMode = false;

  newSubmissionId?: string;

  logInInvalidToken = false;

  contestQuery!: QueryRef<ContestQuery, ContestQueryVariables>;

  getScoreTier = getScoreTier;

  ngOnInit() {
    this.setQuery();
  }

  getContestClock = ({ contest: { material: { startTime, endTime } } }: ContestQuery) =>
    interval(Duration.fromObject({ seconds: 1 }).as('milliseconds')).pipe(
      startWith(0),
      map(() => {
        const now = DateTime.local();
        const start = DateTime.fromISO(startTime);
        const end = DateTime.fromISO(endTime);

        return now < start
          ? {
            status: 'startingIn',
            value: start.diff(now),
          }
          : now < end
            ? {
              status: 'endingIn',
              value: end.diff(now),
            }
            : {
              status: 'endedBy',
              value: now.diff(end),
            };
      }),
    )

  setQuery() {
    this.contestQuery = this.apollo.watchQuery<ContestQuery, ContestQueryVariables>({
      query: gql`
        query ContestQuery($userId: String) {
          serverTime
          contest {
            material {
              ...ContestMaterialFragment
            }
            view(userId: $userId) {
              user {
                id
                displayName
              }
              problemSet {
                problems {
                  ...ProblemFragment
                  view(userId: $userId) {
                    ...ProblemViewFragment
                  }
                }
                totalScoreRange {
                  ...ScoreRangeFragment
                }
                view(userId: $userId) {
                  tackling {
                    totalScore
                  }
                }
              }
            }
          }
        }
        ${contestMaterialFragment}
        ${problemFragment}
        ${problemViewFragment}
        ${scoreRangeFragment}
      `,
      variables: { userId: this.userId },
      pollInterval,
    });
  }

  async setAuth(auth: Auth) {
    await this.authService.setAuth(auth);
    this.setQuery();
  }

  async logIn(event: Event, modal: NgbActiveModal) {
    const formData = new FormData(event.target as HTMLFormElement);
    const { data } = await this.apollo.mutate<LoginMutation, LoginMutationVariables>({
      mutation: gql`
        mutation LoginMutation($token: String!) {
          auth(token: $token) {
            token
            userId
          }
        }
      `,
      variables: {
        token: formData.get('token') as string,
      },
    }).toPromise();

    if (data === null || data === undefined) { throw Error('error during login'); }

    if (data.auth === null) {
      this.logInInvalidToken = true;

      return;
    }

    const { token, userId } = data.auth;

    if (userId === null) {
      throw new Error(`login successful but no userId!`);
    }

    await this.setAuth({ token, userId });
    modal.close();
  }
}

