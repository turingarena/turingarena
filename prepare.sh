set -ex

( cd server/ ; npm ci )
( cd web/ ; npm ci )
