import { Component, ViewEncapsulation } from '@angular/core';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { map, tap } from 'rxjs/operators';
import { currentAuthQuery } from '../config/graphql.module';
import { CurrentAuthQuery, CurrentAuthQueryVariables, MainQuery, MainQueryVariables } from '../generated/graphql-types';
import { mainViewFragment } from './main-view.component';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MainComponent {
  constructor(private readonly apollo: Apollo) {}

  readonly currentAuthRef = this.apollo.watchQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({
    query: currentAuthQuery,
    fetchPolicy: 'cache-only',
  });

  readonly queryRef = this.currentAuthRef.valueChanges.pipe(
    tap(({ data }) => {
      console.log(data);
    }),
    map(({ data }) =>
      this.apollo.watchQuery<MainQuery, MainQueryVariables>({
        query: gql`
          query Main($username: ID) {
            mainView(username: $username) {
              ...MainView
            }
          }

          ${mainViewFragment}
        `,
        variables: {
          username: data?.currentAuth?.user.username ?? null,
        },
        fetchPolicy: 'cache-and-network',
        pollInterval: 30000,
      }),
    ),
  );
}
