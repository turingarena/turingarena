.PHONY: all
all: graphql-schema
	cd web/ && npm ci --ignore-scripts
	cd web/ && npm run prepare
	cd web/ && npm run build
	rm -rf rust/turingarena-contest-webcontent/__generated__/webcontent/
	mkdir -p rust/turingarena-contest-webcontent/__generated__/webcontent/
	cp -r web/dist/turingarena-contest/* rust/turingarena-contest-webcontent/__generated__/webcontent/

	cd rust/ && cargo build

.PHONY: no-web
no-web: graphql-schema
	cd rust/ && cargo build --no-default-features

.PHONY: graphql-schema
graphql-schema:
	mkdir -p __generated__
	( cd rust/turingarena-contest/ && cargo run --no-default-features -- generate-schema ) > __generated__/graphql-schema.json

	mkdir -p rust/turingarena-contest-cli/__generated__/
	cat __generated__/graphql-schema.json > rust/turingarena-contest-cli/__generated__/graphql-schema.json

	mkdir -p web/__generated__/
	cat __generated__/graphql-schema.json > web/__generated__/graphql-schema.json

.PHONY: clean
clean:
	rm -rf rust/target/
	rm -rf web/dist/
	find web/ -name __generated__ | xargs rm -r
	git clean -nxd
