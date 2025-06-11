.PHONY: all

all:
	@for file in src/*.md; do \
		if [ -f "$$file" ]; then \
			basename="$$(basename "$$file" .md)"; \
			cp "$$file" "$${basename}.mdc"; \
		fi; \
	done