import { css, cx } from 'emotion';
import React from 'react';
import { NavLink } from 'react-router-dom';
import { AdminViewFragment } from '../../generated/graphql-types';
import { badgeCss, getBadgeCssByValence } from '../../util/components/badge';
import { FragmentProps } from '../../util/fragment-props';
import { Theme } from '../../util/theme';

export function AdminAside({ data }: FragmentProps<AdminViewFragment>) {
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
      <AdminNavLink name="Contests" to="/admin/contests" badge={data.contest.contestTable.rows.length} />
      <AdminNavLink name="Problems" to="/admin/problems" badge={data.contest.problemTable.rows.length} />
      <AdminNavLink name="Users" to="/admin/users" badge={data.contest.userTable.rows.length} />
      <AdminNavLink name="Submissions" to="/admin/submissions" badge={data.contest.submissionTable.rows.length} />
      <AdminNavLink name="Evaluations" to="/admin/evaluations" badge={data.contest.evaluationTable.rows.length} />
    </aside>
  );
}

function AdminNavLink({ name, to, badge }: { name: string; to: string; badge: number }) {
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
        {badge}
      </span>
    </NavLink>
  );
}
