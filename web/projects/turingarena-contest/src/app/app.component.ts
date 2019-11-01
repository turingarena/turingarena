import { Component } from '@angular/core';
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
  faHourglassHalf,
  faList,
  faPaperPlane,
  faSignInAlt,
  faSignOutAlt,
  faSpinner,
} from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DateTime, Duration } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { ContestQuery, ContestQuery_contestView_problems as ContestProblem } from './__generated__/ContestQuery';
import { Auth, getAuth, setAuth } from './auth';
import { ContestQueryService } from './contest-query.service';
import { LoginDialogComponent } from './login-dialog/login-dialog.component';
import { scoreRanges } from './problem-material';

const pollInterval = 5000;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
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

  constructor(
    private readonly contestQueryService: ContestQueryService,
    readonly modalService: NgbModal,
  ) { }

  get userId() {
    const auth = getAuth();

    return auth !== undefined ? auth.userId : undefined;
  }

  contestQuery = this.contestQueryService.watch({ userId: this.userId }, { pollInterval });

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

  // tslint:disable-next-line: no-magic-numbers
  nowObservable = interval(1000).pipe(
    startWith([0]),
    map(() => DateTime.local()),
  );

  getTaskLetter(index: number) {
    return String.fromCharCode('A'.charCodeAt(0) + index);
  }

  getContestState(data: ContestQuery | undefined) {
    if (data === undefined) { return undefined; }

    const { contestView: { startTime, endTime, problems } } = data;

    const getProblemState = (problem: ContestProblem) => {
      const { tackling } = problem;
      if (tackling === null) { throw new Error(); }

      const getAwardState = ({ name }: { name: string }) => {
        if (tackling === null) { throw new Error(); }

        const scoreState = tackling.scores.find((s) => s.awardName === name);
        const badgeState = tackling.badges.find((s) => s.awardName === name);

        return {
          score: scoreState !== undefined ? scoreState.score as number : 0,
          badge: badgeState !== undefined ? badgeState.badge : false,
        };
      };

      return {
        getAwardState,
        score: scoreRanges(problem).map(getAwardState).map(({ score }) => score).reduce((a, b) => a + b, 0),
        maxScore: scoreRanges(problem).map((s) => s.range.max as number).reduce((a, b) => a + b, 0),
        precision: scoreRanges(problem).map((s) => s.range.precision).reduce((a, b) => Math.max(a, b), 0),
      };
    };

    const problemsState = problems !== null ? problems.map(getProblemState) : [];

    return {
      hasScore: problemsState.length > 0,
      startTime: DateTime.fromISO(startTime),
      endTime: DateTime.fromISO(endTime),
      score: problemsState.map((s) => s.score).reduce((a, b) => a + b, 0),
      maxScore: problemsState.map((s) => s.maxScore).reduce((a, b) => a + b, 0),
      precision: problemsState.map((s) => s.precision).reduce((a, b) => Math.max(a, b), 0),
      getProblemState,
    };
  }

  formatDuration(duration: Duration) {
    return duration.toFormat('hh:mm:ss');
  }

  setAuth(auth: Auth) {
    setAuth(auth);
    this.contestQuery.stopPolling();
    this.contestQuery.resetLastResults();
    // tslint:disable-next-line: no-floating-promises
    this.contestQuery.setVariables({
      userId: this.userId,
    });
    this.contestQuery.startPolling(pollInterval);
  }

  async openLoginDialog() {
    const modalRef = this.modalService.open(LoginDialogComponent);
    const modal = modalRef.componentInstance;

    modal.appComponent = this;

    try {
      await modalRef.result;
    } catch (e) {
      // Dismissed, do nothing
    }
  }

}
