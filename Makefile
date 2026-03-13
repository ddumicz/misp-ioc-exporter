IMAGE_NAME ?= misp-ioc-exporter
DATA_DIR ?= $(PWD)/data

.PHONY: build run-json run-edl run-proxy-edl

build:
	docker build -t $(IMAGE_NAME) .

run-json:
	docker run --rm \
		-e MISP_URL="$(MISP_URL)" \
		-e MISP_API_KEY="$(MISP_API_KEY)" \
		-e MISP_VERIFY_SSL="$(MISP_VERIFY_SSL)" \
		-e MISP_TAGS="$(MISP_TAGS)" \
		-e OUTPUT_FORMAT="json" \
		-v "$(DATA_DIR):/data" \
		$(IMAGE_NAME)


