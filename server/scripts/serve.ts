import { loadConfig } from '../src/config';
import { serve } from '../src/server';

serve(loadConfig());
