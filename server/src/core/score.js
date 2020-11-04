const sqlite3 = require('sqlite3').verbose();

const getScoreForDashboard = async (req, res, next) =>{
  
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
    GROUP by submissions.username, submissions.problem_name
 )
GROUP by  username, problem_name
`;

  // Read all the rows and send them back
  db.all(sql, [], (err, rows) => {
      if (err) {
          throw err;
      }
      res.send(rows);
  });
  db.close();
}

export default getScoreForDashboard ; 