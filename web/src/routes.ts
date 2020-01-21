import { Routes } from '@angular/router';
import { EmptyComponent } from './util/empty.component';

export const routes: Routes = [
  {
    path: '',
    component: EmptyComponent,
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
