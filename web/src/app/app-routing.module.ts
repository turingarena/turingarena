import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ContestViewComponent } from './contest-view/contest-view.component';
import { EmptyComponent } from './empty.component';

const routes: Routes = [
  {
    path: '',
    component: ContestViewComponent,
    children: [
      {
        path: '',
        component: EmptyComponent,
      },
      {
        path: 'problem/:problemName',
        component: EmptyComponent,
      },
    ],
  },
  {
    path: 'admin',
    component: EmptyComponent,
    children: [
      {
        path: '',
        component: EmptyComponent,
        data: {
          adminSection: '',
        },
      },
      {
        path: 'problems',
        component: EmptyComponent,
        data: {
          adminSection: 'problems',
        },
      },
      {
        path: 'contestants',
        component: EmptyComponent,
        data: {
          adminSection: 'contestants',
        },
      },
      {
        path: 'messages',
        component: EmptyComponent,
        data: {
          adminSection: 'messages',
        },
      },
      {
        path: 'submissions',
        component: EmptyComponent,
        data: {
          adminSection: 'submissions',
        },
      },
      {
        path: 'evaluations',
        component: EmptyComponent,
        data: {
          adminSection: 'evaluations',
        },
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
