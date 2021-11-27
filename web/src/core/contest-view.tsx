import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { Route } from 'react-router-dom';
import { ContestViewFragment } from '../generated/graphql-types';
import { hiddenCss } from '../util/components/hidden';
import { FragmentProps } from '../util/fragment-props';
import { ContestViewAside, contestViewAsideFragment } from './contest-view-aside';
import { MediaInline, mediaInlineFragment } from './data/media-inline';
import { textFragment } from './data/text';
import { ProblemViewAside, problemViewAsideFragment } from './problem-view-aside';

export const contestViewFragment = gql`
  fragment ContestView on ContestView {
    contest {
      id
      title {
        ...Text
      }
      statement {
        ...MediaInline
      }
    }

    problemSet {
      problems {
        instance {
          id
          definition {
            id
            baseName
            statement {
              ...MediaInline
            }
          }
        }
        ...ProblemViewAside
      }
    }

    ...ContestViewAside
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${contestViewAsideFragment}
  ${problemViewAsideFragment}
`;

const activeMediaInlineCss = css`
  flex: 1;
  overflow: hidden;
`;

export function ContestView({ data }: FragmentProps<ContestViewFragment>) {
  return (
    <div
      className={css`
        flex: 1 1 0;

        display: flex;
        flex-direction: row;
        overflow: hidden;
      `}
    >
      <ContestViewAside data={data} />
      {data.problemSet !== null &&
        data.problemSet.problems.map(a => (
          <Route key={a.instance.definition.id} path={`/${a.instance.definition.baseName}`}>
            {({ match }) => (
              <>
                <ProblemViewAside className={match !== null ? undefined : hiddenCss} data={a} />
                <div className={match !== null ? activeMediaInlineCss : hiddenCss}>
                  <MediaInline data={a.instance.definition.statement} />
                </div>
              </>
            )}
          </Route>
        ))}
      <Route path="/" exact>
        {({ match }) => (
          <div className={match !== null ? activeMediaInlineCss : hiddenCss}>
            <MediaInline data={data.contest.statement} />
          </div>
        )}
      </Route>
    </div>
  );
}
