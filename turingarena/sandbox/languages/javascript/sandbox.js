const vm = require('vm');
const fs = require('fs');
const readline = require('readline');

let onResolveLine;
let nextLinePromise;

function makeLinePromise() {
    return new Promise((resolve) => { onResolveLine = resolve; })
}
nextLinePromise = makeLinePromise();

readline.createInterface({input: process.stdin}).on('line', (line) => {
    const resolve = onResolveLine;
    const next = makeLinePromise();
    resolve({line, next});
});


async function readLine() {
    const { line, next } = await nextLinePromise
    nextLinePromise = next;
    return line;
}

async function readIntegers() {
    const line = await readLine();
    return line.split(" ").map(x => parseInt(x));
}

// read skeleton and source
const skeleton = fs.readFileSync('skeleton.js', 'utf8');
const source = fs.readFileSync('source.js', 'utf8');

// sandbox context
const sandbox = {
    print: (line) => process.stdout.write('' + line + '\n'),
    log: (line) => process.stderr.write('' + line + '\n'),
    readIntegers: readIntegers,
    exit: () => process.exit(),
    flush: () => {},
    __load_source__: function() {vm.runInContext(source, sandbox);}
};

// create sandbox context
vm.createContext(sandbox);

// execute skeleton in the sandbox
vm.runInContext(skeleton, sandbox);

Promise.resolve().then(() => {
    return sandbox.init();
}).then(() => {
    return sandbox.main();
}).then(() => {
    process.exit(0);
})
