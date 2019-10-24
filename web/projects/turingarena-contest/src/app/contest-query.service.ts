import { Injectable } from '@angular/core';
import gql from 'graphql-tag';
import { Query } from 'apollo-angular';
import { ContestQuery } from './__generated__/ContestQuery';

@Injectable({
  providedIn: 'root'
})
export class ContestQueryService extends Query<ContestQuery> {
  document = gql`
    query ContestQuery {
      problems {
        name
        material {
          attachments {
            title {
              value
            }
            file {
              name
              type
            }
          }
        }
      }
    }
  `;
}
