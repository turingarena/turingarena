import { Component, OnInit } from '@angular/core';
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

import { Auth, AuthService } from '../auth.service';
import { contestViewFragment, getContestState } from '../contest';
import { getProblemState } from '../problem';
import { getScoreTier } from '../score';

import { ContestQuery, ContestQueryVariables } from './__generated__/ContestQuery';
import { LoginMutation, LoginMutationVariables } from './__generated__/LoginMutation';
import { getSubmissionState } from '../submission';

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
    readonly modalService: NgbModal,
  ) { }

  get userId() {
    const auth = this.authService.getAuth();

    return auth !== undefined ? auth.userId : undefined;
  }

  get selectedProblemName() {
    try {
      const selectedProblemNameJson = localStorage.getItem('selectedProblemName');

      if (selectedProblemNameJson === null) { return undefined; }

      return JSON.parse(selectedProblemNameJson) as string;
    } catch (e) {
      localStorage.removeItem('selectedProblemName');
    }
  }

  set selectedProblemName(name: string | undefined) {
    localStorage.setItem('selectedProblemName', JSON.stringify(name));
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

  getContestState = getContestState;
  getProblemState = getProblemState;
  getSubmissionState = getSubmissionState;
  getScoreTier = getScoreTier;

  ngOnInit() {
    this.setQuery();
  }

  setQuery() {
    this.contestQuery = this.apollo.watchQuery<ContestQuery, ContestQueryVariables>({
      query: gql`
        query ContestQuery($userId: UserId) {
          serverTime
          contestView(userId: $userId) { ...ContestViewFragment }
        }
        ${contestViewFragment}
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
    } else {
      this.logInInvalidToken = false;
      const { token, userId } = data.auth;

      await this.setAuth({ token, userId });
      modal.close();
    }
  }


}

