PYTHON_VERSIONS := 3.8 3.12
CONTAINER_TOOL := $(shell command -v podman 2> /dev/null || echo docker)

.PHONY: build run clean

build:
	@for version in $(PYTHON_VERSIONS); do \
		echo "Building Python $$version container:"; \
		$(CONTAINER_TOOL) build --build-arg PYTHON_VERSION=$$version -t regex-file-search:$$version .; \
	done

run:
	@for version in $(PYTHON_VERSIONS); do \
		echo "Running tests for Python $$version:"; \
		$(CONTAINER_TOOL) run --rm -v $(PWD):/app -w /app regex-file-search:$$version; \
	done

clean:
	@for version in $(PYTHON_VERSIONS); do \
		echo "Removing Python $$version container: "; \
		$(CONTAINER_TOOL) rmi regex-file-search:$$version; \
	done