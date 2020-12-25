import { gql, useQuery } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
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
              submission: `${sub.files[0].fileName}`,
              download: (
                <Button variant="light" size="sm">
                  <a href={`files/${sub.files[0].contentId}/${sub.files[0].fileName}`}>
                    <FontAwesomeIcon icon="download" />
                  </a>
                </Button>
              ),
              createdate: new Date(sub.createdAt.millisFromEpochInteger + 32400000).toLocaleString(), //TODO: fix timezone offset
            }),
          );
        }
      }),
    );

    return (
      <div>
        <PivotTableUI
          data={pivotSubmission}
          vals={['score']}
          rows={['username', 'problem_name', 'submission', 'createdate', 'download']}
          cols={[]}
          aggregatorName={'Maximum'}
          onChange={setProps}
          {...props}
        />
      </div>
    );
  }
}
