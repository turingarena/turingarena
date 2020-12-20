import React from 'react';
import { ScoresTable } from './scores-table';
import { SubmissionsTable } from './submissions-table';

export function Dashboard() {
  return (
    <>
      <div>
        <ScoresTable />
        <SubmissionsTable />
      </div>
    </>
  );
}
