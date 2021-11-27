import { gql, useQuery } from '@apollo/client';
import { ICellRendererParams } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-alpine.css';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import React, { useEffect, useState } from 'react';
import { Button, Col, Form } from 'react-bootstrap';
import { ProblemSetUndertaking } from '../generated/graphql-types';
import './dashboard.css';

const SUBMISSIONS_DATA = gql`
  query GetSubmissionsData {
    contests {
      problemSet {
        undertakings {
          user {
            username
          }
          problems {
            instance {
              definition {
                baseName
              }
            }
            submissions {
              createdAt {
                millisFromEpochInteger
              }
              files {
                contentId
                fileName
              }
              totalScore {
                score
              }
            }
          }
        }
      }
    }
  }
`;

interface PivotSubmission {
  username: string;
  problem_name: string;
  score: number;
  submission: string;
  createdate: string;
  download: any;
}

export function SubmissionsTable() {
  const { data, error, loading } = useQuery(SUBMISSIONS_DATA);
  const [pivotSubmission, setPivotSubmission] = useState<PivotSubmission[]>([]);
  const [selectedData, setSelectedData] = useState<PivotSubmission[]>([]);
  const [usernames, setUsernames] = useState(['']);
  const [selectedUsername, setSelectedUsername] = useState('All');
  const [problemsNames, setProblemsNames] = useState(['']);
  const [selectedProblemName, setSelectedProblemName] = useState('All');
  const [gridApi, setGridApi] = useState(null);
  const [gridColumnApi, setGridColumnApi] = useState(null);

  function onGridReady(params: any) {
    setGridApi(params.api);
    setGridColumnApi(params.columnApi);
  }

  function LinkComponent(props: ICellRendererParams) {
    return (
      <a href={`files/${props.value.contentId}/${props.value.fileName}`} target="_blank">
        <Button block>Download</Button>
      </a>
    );
  }

  function handleChange(event: any) {
    if (event.target.id === 'username') {
      setSelectedUsername(event.target.value);
    }
    if (event.target.id === 'problem') {
      setSelectedProblemName(event.target.value);
    }
  }

  useEffect(() => {
    const ptmp: PivotSubmission[] = [];
    data?.contests[0].problemSet.undertakings.map((ut: ProblemSetUndertaking) =>
      ut.problems.map(at => {
        if (at.submissions.length > 0) {
          at.submissions.map(sub =>
            ptmp.push({
              username: ut.user.username,
              problem_name: at.instance.definition.baseName,
              score: sub.totalScore?.score ?? 0,
              submission: sub.files[0].fileName,
              download: sub.files[0],
              createdate: new Date(sub.createdAt.millisFromEpochInteger + 32400000).toLocaleString(), //TODO: fix timezone offset
            }),
          );
        }
      }),
    );
    setPivotSubmission(ptmp);
    setSelectedData(ptmp);
    setProblemsNames(
      ptmp.map(entry => entry.problem_name).filter((value, index, self) => self.indexOf(value) === index),
    );
    setUsernames(ptmp.map(entry => entry.username).filter((value, index, self) => self.indexOf(value) === index));
  }, [data]);

  useEffect(() => {
    let tmp = pivotSubmission;
    if (selectedUsername !== 'All') {
      tmp = tmp.filter(value => value.username === selectedUsername);
    }
    if (selectedProblemName !== 'All') {
      tmp = tmp.filter(value => value.problem_name === selectedProblemName);
    }
    setSelectedData(tmp);
  }, [selectedProblemName, selectedUsername]);

  return (
    <>
      <Form onChange={handleChange}>
        <Form.Row>
          <Form.Group as={Col} md="4">
            <Form.Label>Username</Form.Label>
            <Form.Control as="select" id="username">
              <option>All</option>
              {usernames.map(username => (
                <option>{username}</option>
              ))}
            </Form.Control>
          </Form.Group>
          <Form.Group as={Col} md="4">
            <Form.Label>Problem Name</Form.Label>
            <Form.Control as="select" id="problem">
              <option>All</option>
              {problemsNames.map(problem => (
                <option>{problem}</option>
              ))}
            </Form.Control>
          </Form.Group>
        </Form.Row>
      </Form>
      <div className="ag-theme-alpine">
        <AgGridReact
          rowData={selectedData}
          rowSelection="multiple"
          animateRows
          onGridReady={onGridReady}
          frameworkComponents={{
            LinkComponent,
          }}
        >
          <AgGridColumn field="username" sortable={true} headerName="Username" resizable={true} />
          <AgGridColumn field="problem_name" sortable={true} headerName="Problem Name" resizable={true} />
          <AgGridColumn field="createdate" sortable={true} headerName="Submission Date" resizable={true} />
          <AgGridColumn field="score" sortable={true} resizable={true} />
          <AgGridColumn field="submission" headerName="Submission File Name" resizable={true} />
          <AgGridColumn field="download" cellRenderer="LinkComponent" headerName="Download Link" resizable={true} />
        </AgGridReact>
      </div>
    </>
  );
}
