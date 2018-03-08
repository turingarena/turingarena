const vm = require('vm');
const fs = require('fs');
const scanf = require('scanf');

// read skeleton and source
const skeleton = fs.readFileSync('skeleton.js', 'utf8');
const source = fs.readFileSync('source.js', 'utf8');

// function to load source when skeleton invokes a function for the first time
var source_loaded = false;
function load_source() {
    if (!source_loaded) {
        vm.runInContext(source, sandbox);
        source_loaded = true;
    }
}

// get integer
function readInteger() {
    return scanf("%d");
}

// sandbox context
const sandbox = {
    print: console.log,
    readInteger: readInteger,
    exit: process.exit,
    flush: function() {},
    __load_source__: load_source
};

// create sandbox context
vm.createContext(sandbox);

// execute skeleton in the sandbox
vm.runInContext(skeleton, sandbox);

// exit
process.exit(0);
