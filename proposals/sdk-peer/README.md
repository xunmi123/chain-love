# SDK peer requirement proposal fixture

This isolated prototype exercises a proposed optional `peerRequirements` field. It does not alter category CSVs, production schema or automation-owned release columns.

Evidence snapshots: Chain.Love main `d63e7e438588aff29c2b819ff6c34abb7ed6a0ac`; json-tools `830d5f05ae15954c43ef23f4085c83d4548d5431`.

Published artifact sources:

- https://registry.npmjs.org/abitype/1.3.0
- https://registry.npmjs.org/%40filoz%2Fsynapse-react/0.5.0
- https://docs.npmjs.com/cli/v11/configuring-npm/package-json/#peerdependenciesmeta

The two manifest fixture files contain only the name, version, peerDependencies and peerDependenciesMeta fields copied from those artifact responses. The extraction reads both peer fields, preserving constraints and the explicit optional flag. Absent optional metadata means a non-optional declared peer; it does not claim an integration has been executed or that a peer alone makes the SDK usable.

Reproduce using Python and jsonschema 4.26.0:

```sh
git clone https://github.com/Chain-Love/chain-love.git data
git -C data checkout d63e7e438588aff29c2b819ff6c34abb7ed6a0ac
git clone --branch json-tools https://github.com/Chain-Love/chain-love.git tooling
git -C tooling checkout 830d5f05ae15954c43ef23f4085c83d4548d5431
python prototype.py --data-repo data --tools-dir tooling/tools
```

The script writes proposed schema, examples and verification.json in its own directory. It runs 16 shape/source cases, checks the two official manifest fixtures, exercises CSV round-trip, actual converter normalization and offer inheritance, verifies the current SDK row schema rejects the new field, and verifies a locally extended row schema accepts it while still accepting the unchanged original row.

This demonstrates the field design and existing converter behavior. It is not a production integration, a repository-wide migration, upstream SDK execution or a maintainer approval. Source URL identity is checked separately in Python because JSON Schema alone cannot ensure the URL's package and version match sibling fields. No package installation or storage account operation is performed by the prototype.
