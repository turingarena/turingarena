import { css, cx } from 'emotion';
import React from 'react';
import { NavLink } from 'react-router-dom';
import { badgeCss, getBadgeCssByValence } from '../../util/components/badge';
import { Theme } from '../../util/theme';

export function AdminAside() {
  return (
    <aside
      className={css`
        flex: 0 0 auto;
        overflow-y: auto;

        width: 16em;
        padding: 16px;
        background-color: ${Theme.colors.light};
        border-right: 1px solid rgba(0, 0, 0, 0.1);
      `}
    >
      <AdminNavLink name="Users" to="/admin/users" />
    </aside>
  );
}

function AdminNavLink({ name, to }: { name: string; to: string }) {
  return (
    <NavLink
      className={css`
        overflow: hidden;

        margin: 0 -16px;
        padding: 0.5rem 16px;

        display: flex;
        flex-direction: row;
        align-items: center;
        text-decoration: none;
        color: ${Theme.colors.blue};

        &:visited {
          color: ${Theme.colors.blue};
        }

        &:hover {
          text-decoration: none;
          background-color: ${Theme.colors.gray200};
        }
      `}
      activeClassName={css`
        color: ${Theme.colors.white};
        background-color: ${Theme.colors.blue};

        &:visited {
          color: ${Theme.colors.white};
        }

        &:hover {
          text-decoration: none;
          background-color: ${Theme.colors.blue};
        }
      `}
      title={name}
      to={to}
    >
      <span
        className={css`
          text-transform: uppercase;
          margin-right: 10px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          flex: 1 1 auto;
        `}
      >
        {name}
      </span>
      <span
        className={cx(
          css`
            white-space: nowrap;

            & > small.score-range {
              font-weight: inherit;
            }
          `,
          badgeCss,
          getBadgeCssByValence('NOMINAL'),
        )}
      >
        0
      </span>
    </NavLink>
  );
}
