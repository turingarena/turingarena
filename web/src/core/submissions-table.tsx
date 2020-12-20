import { gql, useQuery } from '@apollo/client';
import React, { useState } from 'react';
import PivotTableUI from 'react-pivottable/PivotTableUI';
import { ContestProblemSetUserTackling } from '../generated/graphql-types';
import './dashboard.css';

const SUBMISSIONS_DATA = gql`
  query GetSubmissionsData {
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
            submissions {
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
  submission: any;
}

export function SubmissionsTable() {
  const [props, setProps] = useState(null);

  const { data, error, loading } = useQuery(SUBMISSIONS_DATA);
  const pivotSubmission: PivotSubmission[] = [];

  if (loading) {
    return <></>;
  } else {
    data?.contests[0].problemSet.userTacklings.map((ut: ContestProblemSetUserTackling) =>
      ut.assignmentTacklings.map(at => {
        if (at.submissions.length > 0) {
          at.submissions.map(sub =>
            pivotSubmission.push({
              username: ut.user.username,
              problem_name: at.assignment.problem.name,
              score: sub.totalScore.score,
              submission: (
                <a href={`files/${sub.files[0].contentId}/${sub.files[0].fileName}`}>{sub.files[0].fileName}</a>
              ),
            }),
          );
        }
      }),
    );

    //sub.files[0].contentId,
    return (
      <div>
        <PivotTableUI
          data={pivotSubmission}
          vals={['score']}
          rows={['username', 'problem_name', 'submission']}
          cols={[]}
          aggregatorName={'Maximum'}
          onChange={setProps}
          {...props}
        />
      </div>
    );
  }
}
