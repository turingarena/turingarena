start-server ;

new-session cat ;

set-option destroy-unattached on ;
set-option mouse on ;

# set-option remain-on-exit on ;
# set-hook client-detached kill-session ;
# set-hook pane-died respawn-pane #{hook_pane} ;

set-hook pane-exited kill-window #{hook_window} ;

# attach-session ;

select-layout tiled

split-window -c server/
select-layout tiled

split-window -c web/
select-layout tiled

split-window -c server/ npm run start
select-layout tiled

split-window -c server/ npm run watch:check:test
select-layout tiled

split-window -c server/ npm run watch:check:tslint
select-layout tiled

split-window -c server/ npm run watch:check:tsc
select-layout tiled

split-window -c server/ npm run watch:prepare:graphql-codegen
select-layout tiled

split-window -c web/ npm run start
select-layout tiled

split-window -c web/ npm run watch:prepare
select-layout tiled

split-window -c dashboard-api/ npm run start
select-layout tiled
