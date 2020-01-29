start-server ;

new-session cat ;

set-option destroy-unattached on ;
set-option mouse on ;

# set-option remain-on-exit on ;
# set-hook client-detached kill-session ;
# set-hook pane-died respawn-pane #{hook_pane} ;

set-hook pane-exited kill-window #{hook_window} ;

# attach-session ;

split-window -v -p 33 -t 0 -c server/
split-window -h -t 1 -c web/

split-window -v -t 0 -c server/ npm run start
# split-window -h -t 1 cat # dummy
split-window -h -t 1 -c web/ npm run start
split-window -h -t 2 -c web/ npm run watch:prepare

split-window -v -t 0 -c server/ npm run watch:check:test
split-window -h -t 1 -c server/ npm run watch:check:tslint
split-window -h -t 1 -c server/ npm run watch:check:tsc
split-window -h -t 3 -c server/ npm run watch:prepare:graphql-codegen

kill-pane -t 0

# split-window -h -t 0 -l 1 cat # -c server/
# split-window -h -t 0 -l 1 cat # -c web/
# split-window -h -t 0 -l 1 cat # dummy
# split-window -h -t 0 -l 1 cat # dummy

# kill-pane -t 0

# split-window -h -c server/ npm run watch:lint ;
# split-window -h -c web/ npm run start ;

# select-layout tiled ;
