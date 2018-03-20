const vm = require('vm');
const fs = require('fs');
const scanf = require('scanf');

// read skeleton and source
const skeleton = fs.readFileSync('skeleton.js', 'utf8');
const source = fs.readFileSync('source.js', 'utf8');

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
    __load_source__: function() {vm.runInContext(source, sandbox);}
};

// create sandbox context
vm.createContext(sandbox);

// execute skeleton in the sandbox
vm.runInContext(skeleton, sandbox);

// exit
process.exit(0);
