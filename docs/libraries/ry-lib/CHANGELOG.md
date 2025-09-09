# Changelog - ry-lib

All notable changes to the ry-lib library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [0.2.2] - 2025-09-09

### Added
- Added `--ry-version` command using template variables

### Changed

### Fixed
- Fixed critical bug: `bump` command was calling non-existent `changelog update` (should be `changelog bump`)

### Removed

## [0.2.1] - 2025-09-09

### Changed
- Removed install-hooks command in favor of --hook-snippet pattern
- Updated check-versions to support --hook-snippet option

### Removed
- install-hooks command (replaced with --hook-snippet)

## [0.2.0] - 2025-09-08

### Changed
- Renamed from ry-dev to ry-lib for clarity
- Updated description to focus on library management

## [0.1.0] - 2025-09-08

### Added
- Initial release as ry-dev library
- Basic command structure with test and version commands
