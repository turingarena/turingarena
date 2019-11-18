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
	( cd rust/turingarena/ && cargo run --features contest --bin turingarena-graphql-schema ) > __generated__/graphql-schema.json

	mkdir -p web/__generated__/
	cat __generated__/graphql-schema.json > web/__generated__/graphql-schema.json

.PHONY: clean
clean: clean-generated clean-rust clean-web
	git clean -nxd

.PHONY: clean-generated
clean-generated:
	find ./ -name __generated__ | xargs rm -rf

.PHONY: clean-rust
clean-rust:
	rm -rf rust/target/

.PHONY: clean-web
clean-web:
	rm -rf web/dist/
