.PHONY: all
all:

.PHONY: server
server:
	hugo server --buildDrafts --buildFuture

.PHONY: mdl
mdl:
	markdownlint content/posts

.PHONY: mdlf
mdlf:
	markdownlint --fix content/posts

.PHONY: new-post
new-post: guard-SLUG
	hugo new content/posts/$(shell date +%Y)/$(shell date +%m)/$(SLUG).md

# https://stackoverflow.com/a/7367903
guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi
