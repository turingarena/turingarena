import React from 'react';
import { Tab, Tabs } from 'react-bootstrap';
import { ScoresTable } from './scores-table';
import { SubmissionsTable } from './submissions-table';

export function Dashboard() {
  return (
    <>
      <div style={{ padding: '5px' }}>
        <Tabs defaultActiveKey="scores" id="dashboardTabs">
          <Tab eventKey="scores" title="Scores">
            <div style={{ padding: '30px' }}>
              <ScoresTable />
            </div>
          </Tab>
          <Tab eventKey="submissions" title="Submissions">
            <div style={{ padding: '30px' }}>
              <SubmissionsTable />
            </div>
          </Tab>
        </Tabs>
      </div>
    </>
  );
}
