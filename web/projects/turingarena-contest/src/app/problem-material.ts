import { ProblemMaterialFragment } from './__generated__/ProblemMaterialFragment';

export const scoreRanges = (problem: ProblemMaterialFragment) => problem.material.awards.map(({ name, content }) => {
  if (content.__typename === 'ScoreAwardContent') {
    return { name, range: content.range };
  } else {
    return { name, range: { precision: 0, max: 0 } };
  }
});
