let scanf = require('nodejs-scanf')['scanfSync'];

// read skeleton and source
var fs = require('fs');
var skeleton = fs.readFileSync('skeleton.js', 'utf8');
var source = fs.readFileSync('source.js', 'utf8');

function print(s) {
    console.log(s);
}

var exit = process.exit;

// setto a null quanto non voglio sia accessibile nell'ambiente protetto
require = null;
console = null;
fs = null;
process = Object();

// function to load the source on the first call
var __source_loaded__ = false;
function __load_source__() {
    if (!__source_loaded__) {
        eval(source);
        __source_loaded__ = true;
    }
}

// execute skeleton and source
eval(skeleton);
eval(source);

// run skeleton main()
main();

exit(0);
