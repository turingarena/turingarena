#!/usr/bin/env node

import { loadConfig } from '../src/main/config';
import { serve } from '../src/main/server';

serve(loadConfig('./turingarena.config.json'));
