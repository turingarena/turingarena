import { css, cx } from 'emotion';
import { Valence } from '../../generated/graphql-types';
import { Theme } from '../theme';

export const badgeCss = cx(
  'badge',
  'badge-pill',
  css`
    border: 1px solid transparent;
  `,
);

const badgeCssLight = cx(
  'badge-light',
  css`
    border-color: ${Theme.colors.gray300};
  `,
);
const badgeCssSuccess = cx(
  'badge-success',
  css`
    border-color: transparent;
  `,
);
const badgeCssWarning = cx(
  'badge-warning',
  css`
    border-color: transparent;
  `,
);

export function getBadgeCssByValence(valence: Valence | null) {
  switch (valence) {
    case 'SUCCESS':
      return badgeCssSuccess;
    case 'PARTIAL':
      return badgeCssWarning;
    default:
      return badgeCssLight;
  }
}
