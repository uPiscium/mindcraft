default: validate

validate:
	npx eslint .

lint:
	npx eslint .

test:
	node --test $(rg --files -g '*.test.js')

start:
	npm start
