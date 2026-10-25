#!/usr/bin/env python3
"""Write the OpenAPI document to docs/openapi.json.

CI regenerates it and fails if it differs, so the committed contract always matches the code.
The document describes the template's defaults (session authentication, API enabled), whatever the
environment says. Usage: uv run python scripts/export_openapi.py
"""

import json
import os
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "openapi.json"


def main() -> None:
    os.environ.update(
        {
            "DJANGO_SETTINGS_MODULE": "example_project.settings",
            "EXAMPLE_DEBUG": "true",
            "EXAMPLE_API_ENABLED": "true",
            "EXAMPLE_API_AUTH_MODE": "session",
        }
    )
    import django

    django.setup()
    from drf_spectacular.generators import SchemaGenerator

    schema = SchemaGenerator().get_schema(request=None, public=True)
    OUTPUT.write_text(
        json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
