IMAGE_NAME ?= misp-ioc-exporter
# Obraz w GHCR – ustaw przed push: make push-ghcr GHCR_IMAGE=ghcr.io/USER/misp-ioc-exporter
GHCR_IMAGE ?= ghcr.io/owner/misp-ioc-exporter
IMAGE_TAG ?= latest

.PHONY: build build-ghcr push-ghcr run-json run-edl run-proxy-edl

build:
	docker build -t $(IMAGE_NAME) .

build-ghcr:
	docker build -t $(GHCR_IMAGE):$(IMAGE_TAG) .

push-ghcr: build-ghcr
	docker push $(GHCR_IMAGE):$(IMAGE_TAG)

run-json:
	docker run --rm \
		-e MISP_URL="$(MISP_URL)" \
		-e MISP_API_KEY="$(MISP_API_KEY)" \
		-e MISP_VERIFY_SSL="$(MISP_VERIFY_SSL)" \
		-e MISP_TAGS="$(MISP_TAGS)" \
		-e OUTPUT_FORMAT="json" \
		-v "$(DATA_DIR):/data" \
		$(IMAGE_NAME)


