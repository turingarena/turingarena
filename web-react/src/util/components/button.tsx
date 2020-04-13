import { css } from 'emotion';
import { Theme } from '../theme';

export const buttonPrimaryCss = 'btn-primary';
export const buttonSecondaryCss = 'btn-secondary';
export const buttonLightCss = 'btn-light';

/** Shows a <button> as a simple <div> */
export const buttonNormalizeCss = css`
  text-decoration: none;
  display: inline-block;

  &:focus {
    outline: none;
  }

  background: transparent;
  border: none;
`;

export const buttonCss = 'btn';
