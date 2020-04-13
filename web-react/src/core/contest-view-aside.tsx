import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { Link } from 'react-router-dom';
import { ContestViewAsideFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { ContestViewClock, contestViewClockFragment } from './contest-view-clock';
import { GradeField, scoreFieldFragment } from './fields/grade-field';
import { textFragment } from './text';

// TODO: duplicated?
const headerClass = css`
  text-transform: uppercase;
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
  font-weight: 500;
  line-height: 1.2;
`;

export function ContestViewAside({ data }: FragmentProps<ContestViewAsideFragment>) {
  if (data.problemSetView === null) {
    return null;
  }

  return (
    <>
      <div>
        <h2 className={headerClass}>Score</h2>
        <div
          className={css`
            white-space: nowrap;
            text-align: right;

            font-size: 2rem;
            margin-bottom: 16px;
          `}
        >
          <GradeField data={data.problemSetView.totalScoreField} />
        </div>
      </div>

      <ContestViewClock data={data} />

      <h2 className={headerClass}>Problems</h2>
      <div
        className={css`
          padding: 0;
          list-style: none;
        `}
      >
        {data.problemSetView.assignmentViews.map((assignmentView, index) => (
          <Link
            className={css`
              overflow: hidden;

              margin: 0 -16px;
              padding: 0.5rem 16px;

              display: flex;
              flex-direction: row;

              &:hover {
                text-decoration: none;
              }

              &.active {
                color: #fff;
                background-color: #007bff;
              }
            `}
            key={index}
            // routerLink={['/problem', assignmentView.assignment.problem.name]}
            title={assignmentView.assignment.problem.title.variant}
            to={`/problem/${assignmentView.assignment.problem.name}`}
          >
            <span
              className={css`
                text-transform: uppercase;

                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
              `}
            >
              {assignmentView.assignment.problem.title.variant}
            </span>
            {/* <ContestProblemScore appValence={assignmentView.totalScoreField.valence}> */}
            <span
              className={css`
                margin-left: auto;
              `}
            >
              <GradeField data={assignmentView.totalScoreField} />
            </span>
          </Link>
        ))}
      </div>
    </>
  );
}

export const contestViewAsideFragment = gql`
  fragment ContestViewAside on ContestView {
    problemSetView {
      totalScoreField {
        ...ScoreField
      }

      assignmentViews {
        assignment {
          id
          problem {
            id
            name
            title {
              ...Text
            }
          }
        }
        totalScoreField {
          ...ScoreField
        }
      }
    }

    ...ContestViewClock
  }

  ${textFragment}
  ${scoreFieldFragment}
  ${contestViewClockFragment}
`;
