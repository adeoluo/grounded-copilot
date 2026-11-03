# Changelog

All notable changes to this project are documented here. The file is generated
from Conventional Commits by [git-cliff](https://git-cliff.org) when a release is cut
with `make cut-release`.

## Unreleased

### Features

- Implement grounded copilot with citations, abstention, and faithfulness (#1)

### Bug fixes

- Faithfulness scores zero when the answer cites nothing (#3)

### Documentation

- Clarify that headline metrics come from the offline provider (#2)
- Standard README structure and language framing (#5)
- Vertical layered architecture diagram
- Clarify optional provider in architecture diagram
- Horizontal layered architecture diagram
- Compact horizontal architecture diagram
- Recorded demos of more commands, with their vhs tapes (#1)
- Recorded demos of the HTTP service and more commands (#2)
- Describe the supply chain accurately (#3)

### Build and CI

- Run CodeQL on main and on a weekly schedule only

### Maintenance

- Initialize repository with license and overview
- Remove Dependabot configuration
