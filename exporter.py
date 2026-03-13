import json
import os
import sys
from datetime import datetime, timezone
from typing import List, Any, Dict

from pymisp import PyMISP


def get_env(name: str, required: bool = True, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if required and not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value or ""


def init_misp() -> PyMISP:
    url = get_env("MISP_URL")
    key = get_env("MISP_API_KEY")
    verify_ssl_raw = os.getenv("MISP_VERIFY_SSL", "true").lower()
    verify_ssl = verify_ssl_raw in {"1", "true", "yes", "y"}

    return PyMISP(url, key, ssl=verify_ssl, debug=False)


def fetch_events_by_tags(misp: PyMISP, tags: List[str]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for tag in tags:
        result = misp.search(controller="events", tags=tag, pythonify=True)
        if not result:
            continue
        for event in result:
            events.append(event.to_dict() if hasattr(event, "to_dict") else event)
    return events


def fetch_attributes_by_tags(misp: PyMISP, tags: List[str]) -> List[Dict[str, Any]]:
    attributes: List[Dict[str, Any]] = []
    for tag in tags:
        result = misp.search(controller="attributes", tags=tag, pythonify=True)
        if not result:
            continue
        for attr in result:
            attributes.append(attr.to_dict() if hasattr(attr, "to_dict") else attr)
    return attributes


def extract_iocs(
    events: List[Dict[str, Any]],
    attributes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Wyciągnij atrybuty IOC zarówno z eventów, jak i z wyszukanych atrybutów."""
    iocs: List[Dict[str, Any]] = []

    # Eventy -> wszystkie ich atrybuty
    for event in events:
        event_info = event.get("Event", {})
        event_id = event_info.get("id")
        event_uuid = event_info.get("uuid")
        event_tags = [t.get("name") for t in event_info.get("Tag", []) if t.get("name")]
        for attr in event_info.get("Attribute", []):
            iocs.append(
                {
                    "event_id": event_id,
                    "event_uuid": event_uuid,
                    "event_info": event_info.get("info"),
                    "event_tags": event_tags,
                    "attribute_id": attr.get("id"),
                    "attribute_uuid": attr.get("uuid"),
                    "category": attr.get("category"),
                    "type": attr.get("type"),
                    "value": attr.get("value"),
                    "comment": attr.get("comment"),
                }
            )

    # Pojedyncze atrybuty znalezione po tagu (np. tag tylko na atrybucie)
    for item in attributes:
        attr_wrapper = item.get("Attribute", item)
        event_info = attr_wrapper.get("Event", {}) or item.get("Event", {})

        event_id = event_info.get("id")
        event_uuid = event_info.get("uuid")
        event_tags = [t.get("name") for t in event_info.get("Tag", []) if t.get("name")] if event_info else []

        iocs.append(
            {
                "event_id": event_id,
                "event_uuid": event_uuid,
                "event_info": event_info.get("info") if event_info else None,
                "event_tags": event_tags,
                "attribute_id": attr_wrapper.get("id"),
                "attribute_uuid": attr_wrapper.get("uuid"),
                "category": attr_wrapper.get("category"),
                "type": attr_wrapper.get("type"),
                "value": attr_wrapper.get("value"),
                "comment": attr_wrapper.get("comment"),
            }
        )

    return iocs


def main() -> None:
    raw_tags = get_env("MISP_TAGS")
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    if not tags:
        print("MISP_TAGS is empty. Provide at least one tag (comma-separated).", file=sys.stderr)
        sys.exit(1)

    output_format = os.getenv("OUTPUT_FORMAT", "json").lower()

    default_output = "/data/iocs.json" if output_format == "json" else "/data/iocs.edl"
    output_path = os.getenv("OUTPUT_PATH", default_output)

    misp = init_misp()
    events = fetch_events_by_tags(misp, tags)
    attributes = fetch_attributes_by_tags(misp, tags)
    iocs = extract_iocs(events, attributes)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if output_format == "edl":
        # EDL: jedna wartość IOC na linię, unikalnie, bez duplikatów.
        values = sorted({ioc["value"] for ioc in iocs if ioc.get("value")})
        with open(output_path, "w", encoding="utf-8") as f:
            generated_at = datetime.now(timezone.utc).isoformat()
            f.write(f"# generated_at={generated_at}Z; tags={','.join(tags)}\n")
            for v in values:
                f.write(f"{v}\n")
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(iocs, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(iocs)} IOCs to {output_path} in format {output_format}")


if __name__ == "__main__":
    main()
