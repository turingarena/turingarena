const { json } = require("express");
var express = require("express");
var router = express.Router();
const fs = require('fs');
const yaml = require('js-yaml');
const fetch = require("node-fetch");
const sqlite3 = require('sqlite3').verbose();




router.get('/', async function(req, res, next) {
  // open the database
  let db = new sqlite3.Database('/home/aslan/Desktop/turingarena/server/db.sqlite3',sqlite3.OPEN_READONLY,(err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Connected to the database.');
  });

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

  var dati
  db.all(sql, [], (err, rows) => {
    if (err) {
      throw err;
    }
    console.log(rows)
    res.send(rows)
  });
  db.close();
  
  });

module.exports = router;