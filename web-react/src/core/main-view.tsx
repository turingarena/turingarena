import { gql } from '@apollo/client';
import React from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import { MainViewFragment } from '../generated/graphql-types';
import { ContestView, contestViewFragment } from './contest-view';
import { TopBar, topBarFragment } from './top-bar';

export const mainViewFragment = gql`
  fragment MainView on MainView {
    ...TopBar
    contestView {
      ...ContestView
    }
  }

  ${topBarFragment}
  ${contestViewFragment}
`;

function Home() {
  return <h1>Home</h1>;
}

export function MainView({ data }: { data: MainViewFragment }) {
  const hasDefaultContest = true;

  return (
    <BrowserRouter>
      <TopBar data={data} />
      <Switch>
        {!hasDefaultContest ? (
          <Route path="/:contest">
            <ContestView />
          </Route>
        ) : undefined}
        <Route path="/">{hasDefaultContest ? <ContestView /> : <Home />}</Route>
      </Switch>
    </BrowserRouter>
  );
}
