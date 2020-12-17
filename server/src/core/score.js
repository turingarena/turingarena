import {isLogged} from './auth';
const sqlite3 = require('sqlite3').verbose();

/**
 * Interrogate the database and returns the maximum score made by each player for each problem.
 * The data are served only if the user is logged
 * @returns a Json array where evry line contains the user that made the submission,
 *  the problem name and the score made
 */
export const getUsersScore = async (req, res, next) =>{

    if(!isLogged(req)){
      res.json([{}]);
      return;
    }

    // Open the database in ReadOnly mode.
    let db = new sqlite3.Database(
      (__dirname.slice(0,-8)+'db.sqlite3'), // i cannot find a better way to get the file
        sqlite3.OPEN_READONLY,
        err => {
            if (err) {
                console.error(err);
            }else{
            console.log('Connected to the database.');
            }
        },
    );

    // For each player select the best score that they have made in a problem
    let sql = `
    SELECT username, problem_name, max(score) as score
  FROM(
    SELECT submissions.username, submissions.problem_name, sum (achievements.grade) as score
      from submissions
      JOIN evaluations on submissions.id = evaluations.submission_id
      JOIN achievements on achievements.evaluation_id = evaluations.id
      GROUP by submissions.username, submissions.problem_name, submissions.id
  )
  GROUP by  username, problem_name
  `;

    // Read all the rows and send them back
    db.all(sql, [], (err, rows) => {
        if (err) {
            throw err;
            res.json([{}]);
        }
        res.json(rows);
    });
    db.close();

}
