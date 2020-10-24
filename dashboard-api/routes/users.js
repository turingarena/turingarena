var express = require('express');
var router = express.Router();
const fs = require('fs');
const yaml = require('js-yaml');

function getconfig(){
  try {
    let fileContents = fs.readFileSync('turingarena.yaml', 'utf8');
    let data = yaml.safeLoad(fileContents);
  
    console.log(data);
  } catch (e) {
    console.log(e);
  }
  return "ciao";
}



/* GET users listing. */
router.get('/', function(req, res, next) {
  var data

  // try to load the data from the copy of the .yaml file
  try {
    let fileContents = fs.readFileSync('turingarena.yaml', 'utf8');
    data = yaml.safeLoad(fileContents);

    console.log(data);
  } catch (e) {
    console.log(e);
  }

  users = data.users;
  
  // hide the password of the users and define a role for every user
  users.forEach(element => {
    element.role = element.role !== undefined ? element.role : "user"
    element.token = undefined
  });
  res.send(users);
});

module.exports = router;
