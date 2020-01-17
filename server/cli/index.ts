import * as commander from 'commander';
import { _import } from './import';

const program = new commander.Command();

function serve() {
}

function _export() {

}

function show() {

}

program
    .name('turingarena')
    .option('-c, --config', 'configuration file')
    .version('1.0');

program
    .command('serve')
    .description('start TuringArena server')
    .action(serve);

program
    .command('import [dir]')
    .description('import a contest')
    .action(_import)

program
    .command('export')
    .description('export a contest')
    .action(_export)

program
    .command('show')
    .description('show information about a contest')
    .action(show)

program.parse(process.argv);

