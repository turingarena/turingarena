import { css } from 'emotion';
import React from 'react';
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
  color: '#292b2c';
  border-color: '#292b2c';

  &:hover {
    background-color: '#e7e7e7';
  }
`;

export const buttonCss = css`
  border-radius: 4px;
  padding: 5px 10px;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  transition: 0.3s;
  border-width: 0.5px;

  &:focus {
    outline: none;
    border-color: #292b2c;
  }
`;
