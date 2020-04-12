import { gql } from '@apollo/client';
import React from 'react';
import styled from 'styled-components';
import { ContestViewAsideFragment } from '../generated/graphql-types';
import { ContestViewClock, contestViewClockFragment } from './contest-view-clock';
import { GradeField, scoreFieldFragment } from './grade-field';
import { textFragment } from './text';

// TODO: duplicated?
const AsideHeader = styled.h2`
  text-transform: uppercase;
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
  font-weight: 500;
  line-height: 1.2;
`;

const ContestScore = styled.div`
  white-space: nowrap;
  text-align: right;

  font-size: 2rem;
  margin-bottom: 16px;
`;

const ScoreView = (data: ContestViewAsideFragment) => {
  if (data.problemSetView === null) {
    return null;
  }

  const score = data.problemSetView.totalScoreField.score;

  return (
    <div>
      <AsideHeader>Score</AsideHeader>
      <ContestScore>
        <GradeField data={data.problemSetView.totalScoreField} />
      </ContestScore>
    </div>
  );
}

const ContestProblemList = styled.div`
  padding: 0;
  list-style: none;
`;

const ContestProblemLink = styled.a`
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
`;

const ContestProblemLinkName = styled.span`
  text-transform: uppercase;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ContestProblemScore = styled.span`
  margin-left: auto;
`;

export function ContestViewAside({ data }: { data: ContestViewAsideFragment }) {
  if (data.problemSetView === null) {
    return null;
  }

  return (
    <>
      <div>
        <AsideHeader>Score</AsideHeader>
        <ContestScore>
          <GradeField data={data.problemSetView.totalScoreField} />
        </ContestScore>
      </div>

      <ContestViewClock data={data} />

      <AsideHeader>Problems</AsideHeader>
      <ContestProblemList>
        {data.problemSetView.assignmentViews.map((assignmentView, index) => (
          <ContestProblemLink
            key={index}
            // routerLink={['/problem', assignmentView.assignment.problem.name]}
            // routerLinkActive="active"
            title={assignmentView.assignment.problem.title.variant}
          >
            <ContestProblemLinkName>
              {assignmentView.assignment.problem.title.variant}
            </ContestProblemLinkName>
            <ContestProblemScore appValence={assignmentView.totalScoreField.valence}>
              <GradeField data={assignmentView.totalScoreField} />
            </ContestProblemScore>
          </ContestProblemLink>
        ))}
      </ContestProblemList>
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
