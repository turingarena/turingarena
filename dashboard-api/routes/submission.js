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

  let sql = `SELECT submissions.username, submissions.problem_name, sum (achievements.grade) as score, min (submissions.created_at) as created_at, submission_files.content_id, submission_files.file_name
  from submissions 
  JOIN evaluations on submissions.id = evaluations.submission_id
  JOIN achievements on achievements.evaluation_id = evaluations.id
  JOIN submission_files on submission_files.submission_id = submissions.id
  GROUP by submissions.username, submissions.problem_name, submission_files.content_id, submission_files.file_name`;

  var dati
  db.all(sql, [], (err, rows) => {
    if (err) {
      throw err;
    }
    dati=rows
    rows.forEach((row) => {
      row.solution="http://localhost:3001/files/"+row.content_id+"/"+row.file_name;
      row.file_name=undefined;
      row.content_id=undefined
    });
    res.send(rows)
  });
  db.close();
  
  });

module.exports = router;

/*
  fetch("http://localhost:3000/graphql", {
    body: "{\"query\":\"{mainView{title{variant}}}\"}",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      Dnt: "1"
    },
    method: "POST"
  }).then( res => res.json() )
  .then( data => data);*/

  /*
  const data = await (await fetch("http://localhost:3000/graphql", {
    body: "{\"query\":\"{mainView{title{variant}}}\"}",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      Dnt: "1"
    },
    method: "POST"
  })
  ).json()

  res.send(data)
  });
  */