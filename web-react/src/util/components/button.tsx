import { css } from 'emotion';
import { Theme } from '../theme';

export const buttonPrimaryCss = css`
  background-color: ${Theme.colors.primary};
  color: '#f7f7f7';
  border-color: '#f7f7f7';

  &:hover {
    background-color: '#004e91';
  }
`;

export const buttonLightCss = css`
  background-color: ${Theme.colors.gray100};
  color: '#292b2c';
  border-color: '#292b2c';

  &:hover {
    background-color: '#e7e7e7';
  }
`;

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

export const buttonCss = css`
  ${buttonNormalizeCss}

  border-radius: 4px;
  padding: 5px 10px;
  font-size: 14px;
  transition: 0.3s;
  border: 1px solid transparent;

  text-align: center;
  vertical-align: middle;
  user-select: none;
  cursor: pointer;

  &:focus {
    outline: none;
  }
`;
