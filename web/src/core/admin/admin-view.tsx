import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';
import { AdminViewFragment } from '../../generated/graphql-types';
import { AdminAside } from './admin-aside';
import { AdminTopBar } from './admin-top-bar';
import { Table, tableFragment } from './table';

export const adminViewFragment = gql`
  fragment AdminView on Query {
    contest(id: "default") {
      id
      userTable {
        ...Table
      }
    }
  }

  ${tableFragment}
`;

export function AdminView({ data }: { data: AdminViewFragment }) {
  return (
    <div
      className={css`
        display: flex;
        flex-direction: column;
        height: 100%;
      `}
    >
      <AdminTopBar />
      <div
        className={css`
          flex: 1 1 0;

          display: flex;
          flex-direction: row;
          overflow: hidden;
        `}
      >
        <AdminAside />
        <Switch>
          <Route path="/admin" exact>
            Admin
          </Route>
          <Route path="/admin/users">
            <Table data={data.contest.userTable} />
          </Route>
          <Redirect to="/admin" />
        </Switch>
      </div>
    </div>
  );
}
