import { Component } from '@angular/core';
import { faCheck, faFilePdf, faList, faPaperPlane, faSignInAlt, faSignOutAlt, faHistory } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DateTime, Duration } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { Auth, getAuth, setAuth } from './auth';
import { ContestQueryService } from './contest-query.service';
import { LoginDialogComponent } from './login-dialog/login-dialog.component';
import { scoreRanges } from './problem-material';
import { SubmissionListDialogComponent } from './submission-list-dialog/submission-list-dialog.component';
import { SubmitDialogComponent } from './submit-dialog/submit-dialog.component';
import { ContestQuery_contestView_problems as ContestProblem } from './__generated__/ContestQuery';
import { SubmissionDialogComponent } from './submission-dialog/submission-dialog.component';
import { SubmissionListQuery_contestView_problem_submissions as Submission } from './__generated__/SubmissionListQuery';
import { SubmissionQueryService } from './submission-query.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  faPaperPlane = faPaperPlane;
  faCheck = faCheck;
  faSignInAlt = faSignInAlt;
  faSignOutAlt = faSignOutAlt;
  faList = faList;
  faFilePdf = faFilePdf;
  faHistory = faHistory;

  constructor(
    private contestQueryService: ContestQueryService,
    private submissionQueryService: SubmissionQueryService,
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

        const getAwardState = ({ name }) => {
          const scoreState = problem.scores.find((s) => s.awardName === name);
          const badgeState = problem.badges.find((s) => s.awardName === name);
          return {
            score: scoreState ? scoreState.score : 0,
            badge: badgeState ? badgeState.badge : false,
          };
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
    this.contestQuery.resetLastResults();
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

  // FIXME: repeated code
  async openSubmission(submission: Submission) {
    const modalRef = this.modal.open(SubmissionDialogComponent, { size: 'lg' });
    const modal = modalRef.componentInstance;

    modal.appComponent = this;
    modal.problemName = this.selectedProblemName;
    modal.setSubmissionQueryRef(this.submissionQueryService.watch({
      submissionId: submission.id,
    }, {
        pollInterval: 1000,
      }));

    try {
      await modalRef.result;
    } catch (e) {
      // No-op
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
