import { css } from 'emotion';

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
export const buttonPrimaryCss = 'btn-primary';
export const buttonSecondaryCss = 'btn-secondary';
export const buttonSuccessCss = 'btn-success';
export const buttonLightCss = 'btn-light';
export const buttonBlockCss = 'btn-block';
export const buttonOutlineDarkCss = 'btn-outline-dark';
export const buttonOutlineSecondaryCss = 'btn-outline-secondary';
export const buttonSmallCss = 'btn-sm';
