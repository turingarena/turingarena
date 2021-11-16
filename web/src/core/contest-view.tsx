import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { ContestViewFragment } from '../generated/graphql-types';
import { hiddenCss } from '../util/components/hidden';
import { FragmentProps } from '../util/fragment-props';
import { PathRouter } from '../util/paths';
import {
  ProblemViewAside,
  problemViewAsideFragment,
} from './contest-problem-assignment-view-aside';
import { ContestViewAside, contestViewAsideFragment } from './contest-view-aside';
import { MediaInline, mediaInlineFragment } from './media-inline';
import { textFragment } from './text';

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
            name
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
          <PathRouter key={a.instance.definition.id} path={`/${a.instance.definition.name}`}>
            {({ match }) => (
              <>
                <ProblemViewAside className={match !== null ? undefined : hiddenCss} data={a} />
                <div className={match !== null ? activeMediaInlineCss : hiddenCss}>
                  <MediaInline data={a.instance.definition.statement} />
                </div>
              </>
            )}
          </PathRouter>
        ))}
      <PathRouter path="/" exact>
        {({ match }) => (
          <div className={match !== null ? activeMediaInlineCss : hiddenCss}>
            <MediaInline data={data.contest.statement} />
          </div>
        )}
      </PathRouter>
    </div>
  );
}
