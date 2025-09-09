# Changelog - uv

All notable changes to the uv library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [0.1.1] - 2025-09-09

### Added
- Strict fail-early checks for build command
- Workspace support via native --package flags
- Git tag verification for publish command
- Token auto-loading from pass for publish

### Changed
- Enhanced version bump with package-aware changelog detection
- Build now fails if dist/ is not empty
- Publish now verifies tag is pushed to origin
- Replaced Unicode arrows with ASCII (→ to ->)

### Fixed
- Package detection for workspace projects
- Version detection from wheel and sdist files

## [0.1.0] - 2025-09-08

### Added
- Initial release of uv library
- Basic command structure with test and version commands
