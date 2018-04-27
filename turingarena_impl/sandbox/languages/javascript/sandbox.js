const vm = require('vm');
const fs = require('fs');
const readline = require('readline');

/*
    Creates a promise which resolves to {line, next},
    where line is the next line received in input,
    and next is a promise defined recursively (for successive lines).
*/
function createLineStream() {
    let onResolve;
    let onReject;
    const createNext = () => new Promise((resolve, reject) => {
        onResolve = resolve;
        onReject = reject;
    });
    readline.createInterface({input: process.stdin}).on('line', (line) => {
        const resolve = onResolve;
        const next = createNext();
        resolve({line, next});
    }).on('close', () => {
        onReject();
    });
    return createNext();
}


let nextLinePromise = createLineStream();

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
const skeleton = fs.readFileSync(process.argv[3], 'utf8');
const source = fs.readFileSync(process.argv[2], 'utf8');

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
}).catch(e => {
    process.exit(1);
}).then(() => {
    process.exit(0);
})
