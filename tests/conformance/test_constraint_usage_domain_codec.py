"""The usage tier travels, and both old shapes fail closed.

No v2 reader is kept. The codec already refuses a foreign schema version by exact
comparison and a wrong graph key set by exact key check, so this asserts that the two
existing mechanisms cover the two ways a payload can be stale rather than adding a third.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.snapshot.instance_graph import (
    INSTANCE_GRAPH_SCHEMA_VERSION,
    InstanceGraphCodecError,
    decode_instance_graph,
    encode_instance_graph,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = "constraint_domain_detached_owner"


@pytest.fixture(scope="module")
def encoded() -> bytes:
    return encode_instance_graph(elaborate_model_paths([Path(FIXTURES_DIR / FIXTURE)]))


def test_the_schema_version_is_v3():
    assert INSTANCE_GRAPH_SCHEMA_VERSION == "instance-graph/v3"


def test_round_trip_preserves_every_usage_record_field(encoded):
    live = elaborate_model_paths([Path(FIXTURES_DIR / FIXTURE)])
    rebuilt = decode_instance_graph(encoded)
    assert rebuilt.constraint_usages == live.constraint_usages
    assert encode_instance_graph(rebuilt) == encoded


def test_v2_payload_fails_closed(encoded):
    stale = encoded.replace(b'"instance-graph/v3"', b'"instance-graph/v2"')
    with pytest.raises(InstanceGraphCodecError, match="instance-graph/v3"):
        decode_instance_graph(stale)


def test_v3_payload_missing_the_tier_fails_closed(encoded):
    document = json.loads(encoded)
    del document["graph"]["constraint_usages"]
    with pytest.raises(InstanceGraphCodecError, match="constraint_usages"):
        decode_instance_graph(json.dumps(document).encode())


def test_the_tier_is_inside_the_document_fingerprint(encoded):
    document = json.loads(encoded)
    (row,) = [
        item
        for item in document["graph"]["constraint_usages"]
        if item["usage_qualified_name"].endswith("vacuous_gate")
    ]
    row["disposition"]["severity"] = "info"
    with pytest.raises(InstanceGraphCodecError, match="fingerprint"):
        decode_instance_graph(json.dumps(document).encode())
