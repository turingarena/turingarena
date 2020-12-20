import { gql, useQuery } from '@apollo/client';
import React, { useState } from 'react';
import PivotTableUI from 'react-pivottable/PivotTableUI';
import { ContestProblemSetUserTackling } from '../generated/graphql-types';
import './dashboard.css';

const SCORES_DATA = gql`
  query GetScoresData {
    contests {
      problemSet {
        userTacklings {
          user {
            username
          }
          assignmentTacklings {
            assignment {
              problem {
                name
              }
            }
            scoreGrade {
              score
              scoreRange {
                max
              }
            }
          }
        }
      }
    }
  }
`;

interface PivotScore {
  username: string;
  problem_name: string;
  score: number;
}

/**
 * Returns a PivotTable filled with the scores of the users
 */
export function Scores() {
  const [props, setProps] = useState(null);

  const { data, error, loading } = useQuery(SCORES_DATA);
  const pivotScores: PivotScore[] = [];

  if (loading) {
    return <></>;
  } else {
    data?.contests[0].problemSet.userTacklings.map((ut: ContestProblemSetUserTackling) =>
      ut.assignmentTacklings.map(at =>
        pivotScores.push({
          username: ut.user.username,
          problem_name: at.assignment.problem.name,
          score: at.scoreGrade.score,
        }),
      ),
    );
    console.log(pivotScores.toString());

    return (
      <div>
        <PivotTableUI
          data={pivotScores}
          vals={['score']}
          rows={['username']}
          cols={['problem_name']}
          aggregatorName={'Integer Sum'}
          rendererName={'Table Heatmap'}
          tableColorScaleGenerator={(values: number[]) => {
            const min = Math.min.apply(Math, values);
            const max = Math.max.apply(Math, values);

            return (x: number) => {
              const percentage = (x - min) / (max - min);
              const red = Math.round(255 - percentage * 70);
              const green = Math.round(percentage * 255);

              return { backgroundColor: `rgb(${red},${green},0)` };
            };
          }}
          onChange={setProps}
          {...props}
        />
      </div>
    );
  }
}
