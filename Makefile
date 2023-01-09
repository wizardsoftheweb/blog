.PHONY: all
all:

.PHONY: server
server:
	hugo server --buildDrafts --buildFuture

.PHONY: mdl
mdl:
	markdownlint content/posts
