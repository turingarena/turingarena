import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import { Link } from 'react-router-dom';
import { Theme } from '../../util/theme';

export function AdminTopBar() {
  return (
    <>
      <nav
        className={css`
          display: flex;
          background-color: ${Theme.colors.orange};
          align-items: center;
          padding: 8px 16px;
          color: #fff;
        `}
      >
        <Link
          to="/admin"
          className={css`
            display: block;

            margin: -8px 0;
            padding: 8px 0;

            color: white;
            text-decoration: none;
            background-color: transparent;

            &:hover {
              text-decoration: none;
              color: white;
            }

            margin-right: auto;
          `}
        >
          <h1
            className={css`
              display: block;
              margin: 0;
              font-size: 1.25rem;
              font-weight: 400;
              line-height: inherit;
              white-space: nowrap;
            `}
          >
            <FontAwesomeIcon icon="home" /> Admin
          </h1>
        </Link>
      </nav>
    </>
  );
}
