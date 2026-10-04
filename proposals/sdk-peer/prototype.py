"""Isolated DBIP fixture; does not modify Chain.Love CSVs or production schema."""
import copy
import argparse
import csv
import importlib.util
import io
import json
from pathlib import Path
from urllib.parse import quote

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data-repo", type=Path, required=True)
parser.add_argument("--tools-dir", type=Path, required=True)
args = parser.parse_args()
PACKAGE_PATTERN = r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$"
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": ["object", "null"],
    "additionalProperties": False,
    "properties": {
        "package": {"type": "string", "pattern": PACKAGE_PATTERN},
        "version": {"type": "string", "pattern": r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"},
        "source": {"type": "string", "pattern": r"^https://registry\.npmjs\.org/[^?#]+/[^/?#]+$"},
        "requirements": {
            "type": "object", "minProperties": 1,
            "propertyNames": {"pattern": PACKAGE_PATTERN},
            "additionalProperties": {
                "type": "object", "additionalProperties": False,
                "required": ["constraint", "optional"],
                "properties": {
                    "constraint": {"type": "string", "pattern": r"\S"},
                    "optional": {"type": "boolean"},
                },
            },
        },
    },
    "required": ["package", "version", "source", "requirements"],
}
Draft202012Validator.check_schema(SCHEMA)
validator = Draft202012Validator(SCHEMA)


def source_url(name, version):
    return "https://registry.npmjs.org/" + quote(name, safe="") + "/" + quote(version, safe="")


def extract(manifest):
    peers = manifest.get("peerDependencies", {})
    if not peers:
        return None
    meta = manifest.get("peerDependenciesMeta") or {}
    return {
        "package": manifest["name"], "version": manifest["version"],
        "source": source_url(manifest["name"], manifest["version"]),
        "requirements": {
            name: {"constraint": constraint, "optional": meta.get(name, {}).get("optional", False)}
            for name, constraint in sorted(peers.items())
        },
    }


def valid(value):
    if not validator.is_valid(value):
        return False
    return value is None or value["source"] == source_url(value["package"], value["version"])


fixtures = {}
for slug, filename in [("abitype", "abitype-1.3.0.json"), ("synapse-react", "synapse-react-0.5.0.json")]:
    manifest = json.loads((HERE / filename).read_text(encoding="utf-8"))
    value = extract(manifest)
    assert valid(value)
    assert len(value["requirements"]) == (2 if slug == "abitype" else 4)
    assert all(x["optional"] is (slug == "abitype") for x in value["requirements"].values())
    fixtures[slug] = value

seed = fixtures["abitype"]
cases = [("unknown/null", None, True), ("empty object", {}, False)]


def changed(label, transform):
    value = copy.deepcopy(seed)
    transform(value)
    cases.append((label, value, False))


changed("missing package", lambda x: x.pop("package"))
changed("unknown top-level key", lambda x: x.update({"scope": "peer"}))
changed("empty requirements", lambda x: x.update({"requirements": {}}))
changed("missing optional flag", lambda x: x["requirements"]["zod"].pop("optional"))
changed("string optional flag", lambda x: x["requirements"]["zod"].update({"optional": "true"}))
changed("numeric optional flag", lambda x: x["requirements"]["zod"].update({"optional": 1}))
changed("blank constraint", lambda x: x["requirements"]["zod"].update({"constraint": " "}))
changed("unknown requirement key", lambda x: x["requirements"]["zod"].update({"scope": "dev"}))
changed("URL as package name", lambda x: x["requirements"].update({"https://example.com": {"constraint": "*", "optional": False}}))
changed("unversioned source", lambda x: x.update({"source": "https://registry.npmjs.org/abitype"}))
changed("source version mismatch", lambda x: x.update({"source": "https://registry.npmjs.org/abitype/1.2.3"}))
changed("source package mismatch", lambda x: x.update({"source": "https://registry.npmjs.org/viem/1.3.0"}))
changed("blank version", lambda x: x.update({"version": " "}))
changed("mutable latest tag", lambda x: x.update({"version": "latest", "source": "https://registry.npmjs.org/abitype/latest"}))
for label, value, expected in cases:
    assert valid(value) is expected, label

# Exercise actual repository normalization, offer inheritance and current row schema.
tools_dir = args.tools_dir
spec = importlib.util.spec_from_file_location("converter_fixture", tools_dir / "csv_to_json.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)
result, errors = converter.normalize({"sdks": [{"peerRequirements": ""}, {"peerRequirements": json.dumps(seed)}]})
assert not errors
assert result["sdks"][0]["peerRequirements"] is None
assert result["sdks"][1]["peerRequirements"] == seed
inherited = converter.resolve_offers({"sdks": [{"slug": "abitype", "offer": "!offer:abitype", "peerRequirements": ""}]}, {"sdks": [{"slug": "abitype", "offer": "ABIType", "peerRequirements": seed}]}, network_name="filecoin")
assert inherited["sdks"][0]["peerRequirements"] == seed
stream = io.StringIO(newline="")
writer = csv.writer(stream)
writer.writerow(["peerRequirements"])
writer.writerow([json.dumps(seed, separators=(",", ":"))])
stream.seek(0)
assert json.loads(next(csv.DictReader(stream))["peerRequirements"]) == seed

schema = json.loads((tools_dir / "schema.json").read_text(encoding="utf-8"))
row_schema = schema["$defs"]["sdks"]
rows = list(csv.DictReader((args.data_repo / "references" / "offers" / "sdks.csv").open(encoding="utf-8-sig", newline="")))
normalized, errors = converter.normalize({"sdks": rows})
assert not errors
base_validator = Draft202012Validator(row_schema)
original = next(row for row in normalized["sdks"] if row["slug"] == "abitype")
baseline = copy.deepcopy(original)
baseline["peerRequirements"] = seed
assert not base_validator.is_valid(baseline), "Current schema unexpectedly already supports the proposal"
proposed_row_schema = copy.deepcopy(row_schema)
proposed_row_schema["properties"]["peerRequirements"] = SCHEMA
proposed_validator = Draft202012Validator(proposed_row_schema)
assert proposed_validator.is_valid(original), "Existing row compatibility"
assert proposed_validator.is_valid(baseline), "Proposed field valid"

(HERE / "peer-requirements.schema.json").write_text(json.dumps(SCHEMA, indent=2) + "\n", encoding="utf-8")
(HERE / "fixtures.json").write_text(json.dumps(fixtures, indent=2) + "\n", encoding="utf-8")
report = {"sourceFixtures": 2, "shapeAndSourceCases": len(cases), "normalizationChecks": 2, "offerInheritance": True, "csvRoundTrip": True, "currentSchemaRejectsField": True, "proposedSchemaAcceptsField": True, "existingRowRemainsValid": True, "upstreamCodeExecuted": False, "repositoryCSVsChanged": False}
(HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
