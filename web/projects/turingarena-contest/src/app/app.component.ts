import { Component } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DateTime, Duration } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { ContestQueryService } from './contest-query.service';
import { SubmitDialogComponent } from './submit-dialog/submit-dialog.component';
import {
  ContestQuery_contestView_problems as ContestProblem,
  ContestQuery_contestView_problems_material_awards as Award,
} from './__generated__/ContestQuery';
import { SubmissionListDialogComponent } from './submission-list-dialog/submission-list-dialog.component';
import { LoginDialogComponent } from './login-dialog/login-dialog.component';
import { getAuth, Auth, setAuth } from './auth';
import { faPaperPlane, faSignInAlt, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import { scoreRanges } from './problem-material';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  faPaperPlane = faPaperPlane;
  faSignInAlt = faSignInAlt;
  faSignOutAlt = faSignOutAlt;

  constructor(
    private contestQueryService: ContestQueryService,
    private modal: NgbModal,
  ) { }

  get userId() {
    const auth = getAuth();
    return auth && auth.userId;
  }

  contestQuery = this.contestQueryService.watch({
    userId: this.userId,
  }, {
      pollInterval: 10000,
    });

  get selectedProblemName() {
    return localStorage.getItem('selectedProblemName');
  }

  set selectedProblemName(name: string) {
    localStorage.setItem('selectedProblemName', name);
  }

  nowObservable = interval(1000).pipe(
    startWith([0]),
    map(() => DateTime.local()),
  );

  stateObservable = this.contestQuery.valueChanges.pipe(
    map(({ data }) => {
      if (data === undefined) { return undefined; }

      const { contestView: { startTime, endTime, problems } } = data;

      const getProblemState = (problem: ContestProblem) => {
        if (problem.scores === null) { return; }

        const getAwardState = ({ name }) => problem.scores.find((s) => s.awardName === name) || {
          score: 0,
        };

        return {
          getAwardState,
          score: scoreRanges(problem)
            .map(getAwardState)
            .map((award) => award && award.score || 0)
            .reduce((a, b) => a + b, 0),
          maxScore: scoreRanges(problem).map((s) => s.range.max).reduce((a, b) => a + b, 0),
          precision: scoreRanges(problem).map((s) => s.range.precision).reduce((a, b) => Math.max(a, b), 0),
        };
      };

      const problemsState = problems.map(getProblemState).filter((state) => state !== undefined);

      return {
        hasScore: problemsState.length > 0,
        startTime: DateTime.fromISO(startTime),
        endTime: DateTime.fromISO(endTime),
        score: problemsState.map((s) => s.score).reduce((a, b) => a + b, 0),
        maxScore: problemsState.map((s) => s.maxScore).reduce((a, b) => a + b, 0),
        precision: problemsState.map((s) => s.precision).reduce((a, b) => Math.max(a, b), 0),
        getProblemState,
      };
    })
  );

  formatDuration(duration: Duration) {
    return duration.toFormat('hh:mm:ss');
  }

  setAuth(auth: Auth) {
    setAuth(auth);
    this.contestQuery.stopPolling();
    this.contestQuery.setVariables({
      userId: this.userId,
    });
    this.contestQuery.refetch();
    this.contestQuery.startPolling(10000);
  }

  async openSubmitDialog() {
    const modalRef = this.modal.open(SubmitDialogComponent);
    const modal = modalRef.componentInstance as SubmitDialogComponent;

    modal.appComponent = this;
    modal.problemName = this.selectedProblemName;

    try {
      await modalRef.result;
    } catch (e) {
      // dismissed, do nothing
    }
  }

  async openSubmissionList(problem: ContestProblem) {
    const modalRef = this.modal.open(SubmissionListDialogComponent, { size: 'xl' });
    const modal = modalRef.componentInstance;

    modal.appComponent = this;
    modal.problemName = problem.name;

    try {
      await modalRef.result;
    } catch (e) {
      // dismissed, do nothing
    }
  }

  async openLoginDialog() {
    const modalRef = this.modal.open(LoginDialogComponent);
    const modal = modalRef.componentInstance as LoginDialogComponent;

    modal.appComponent = this;

    try {
      await modalRef.result;
    } catch (e) {
      // dismissed, do nothing
    }
  }

}
