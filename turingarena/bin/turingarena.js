#!/usr/bin/env node

// Require the CLI from the main package, to make it npx compatible
const { cliMain } = require('turingarena-server');

cliMain(process.argv);
