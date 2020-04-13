import { gql } from '@apollo/client';
import { css } from 'emotion';
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
  return (
    <BrowserRouter>
      <div
        className={css`
          display: flex;
          flex-direction: column;
          height: 100%;
        `}
      >
        <TopBar data={data} />
        {data.contestView !== null ? (
          <ContestView data={data.contestView} />
        ) : (
          <Switch>
            <Route path="/">
              <Home />
            </Route>
            <Route path="/:contest">{/* <ContestView data={TODO} /> */}</Route>
          </Switch>
        )}
      </div>
    </BrowserRouter>
  );
}
