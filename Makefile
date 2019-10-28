.PHONY: all
all: rust rust-contest-web-content

.PHONY: rust
rust: graphql-schema
	make just-rust

.PHONY: just-rust
just-rust:
	cd rust/ && cargo build

.PHONY: rust-contest-web-content
rust-contest-web-content: graphql-schema web-content
	make just-rust-contest-web-content

.PHONY: just-rust-contest-web-content
just-rust-contest-web-content:
	cd rust/turingarena-contest/ && cargo build --features web-content

.PHONY: web-content
web-content: web-build
	make just-web-content

.PHONY: just-web-content
just-web-content:
	rm -rf rust/turingarena-contest-web-content/__generated__/web-content/
	mkdir -p rust/turingarena-contest-web-content/__generated__/web-content/
	cp -r web/dist/turingarena-contest/* rust/turingarena-contest-web-content/__generated__/web-content/

.PHONY: web-build
web-build: web-prepare
	make just-web-build

.PHONY: just-web-build
just-web-build:
	cd web/ && npm run build

.PHONY: web-prepare
web-prepare: web-install graphql-schema
	make just-web-prepare

.PHONY: just-web-prepare
just-web-prepare:
	cd web/ && npm run prepare

.PHONY: web-install
web-install:
	cd web/ && npm ci --ignore-scripts

.PHONY: graphql-schema
graphql-schema:
	mkdir -p __generated__
	( cd rust/turingarena-contest/ && cargo run -- generate-schema ) > __generated__/graphql-schema.json

	mkdir -p rust/turingarena-contest-cli/__generated__/
	cat __generated__/graphql-schema.json > rust/turingarena-contest-cli/__generated__/graphql-schema.json

	mkdir -p web/__generated__/
	cat __generated__/graphql-schema.json > web/__generated__/graphql-schema.json

.PHONY: clean
clean:
	rm -rf rust/target/
	rm -rf web/dist/
	find ./ -name __generated__ | xargs rm -r
	git clean -nxd
