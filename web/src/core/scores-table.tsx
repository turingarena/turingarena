import { gql, useQuery } from '@apollo/client';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-alpine.css';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import React, { useEffect, useState } from 'react';
import { ContestProblemSetUserTackling } from '../generated/graphql-types';
import './dashboard.css';

const SCORES_DATA = gql`
  query GetScoresData {
    contests {
      problemSet {
        assignments {
          problem {
            name
          }
        }
        userTacklings {
          user {
            username
          }
          totalScoreGrade {
            score
          }
          assignmentTacklings {
            assignment {
              problem {
                name
              }
            }
            scoreGrade {
              score
            }
          }
        }
      }
    }
  }
`;

export function ScoresTable() {
  const { data, error, loading } = useQuery(SCORES_DATA);
  const [pivotScores, setPivotScores] = useState<Scores[]>([]);
  const [gridApi, setGridApi] = useState(null);
  const [gridColumnApi, setGridColumnApi] = useState(null);
  const [problemsNames, setProblemsNames] = useState<string[]>([]);
  function onGridReady(params: any) {
    setGridApi(params.api);
    setGridColumnApi(params.columnApi);
  }

  interface Scores {
    username: string;
    [key: string]: string;
  }

  const ragCellClassRules = {
    'rag-green': (params: any) => parseInt(params.value, 10) === 100,
    'rag-amber': (params: { value: string }) => parseInt(params.value, 10) < 100 && parseInt(params.value, 10) > 50,
    'rag-red': (params: { value: string }) => parseInt(params.value, 10) <= 50,
  };

  useEffect(() => {
    if (data?.contests[0] !== undefined) {
      const tmpproblemnames: string[] = [];
      data?.contests[0].problemSet.assignments.forEach((a: { problem: { name: any } }) =>
        tmpproblemnames.push(a.problem.name),
      );
      setProblemsNames(tmpproblemnames);

      const tmpScores: Scores[] = [];
      data?.contests[0].problemSet.userTacklings.map((ut: ContestProblemSetUserTackling) => {
        const toAdd: Scores = { username: '' };
        toAdd.username = ut.user.username;
        toAdd.totalScore = ut.totalScoreGrade.score.toString();
        ut.assignmentTacklings.forEach((at, index) => {
          toAdd[tmpproblemnames[index]] = at.scoreGrade.score.toString();
          console.log(tmpproblemnames);
        });
        tmpScores.push(toAdd);
      });
      setPivotScores(tmpScores);
    }
  }, data);

  return (
    <div className="ag-theme-alpine">
      <AgGridReact rowData={pivotScores} rowSelection="multiple" animateRows onGridReady={onGridReady}>
        <AgGridColumn field="username" sortable={true} pinned={'left'} />
        {problemsNames.map((pn: string) => (
          <AgGridColumn field={pn} sortable={true} cellClassRules={ragCellClassRules} />
        ))}
        <AgGridColumn field="totalScore" sortable={true} pinned={'right'} />
      </AgGridReact>
    </div>
  );
}
