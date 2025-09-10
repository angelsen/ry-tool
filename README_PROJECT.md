# ry-tool Project

This repository contains two versions of the ry command augmentation framework:

## ry-next (Current Development)

The next generation implementation with clean architecture and improved design.

- **Location**: `src/ry_next/`
- **Documentation**: `docs_next/ry-next/README.md`
- **Libraries**: `docs_next/libraries/`
- **Examples**: `docs_next/examples/`

### Quick Start
```bash
# Install
pip install -e .

# Run
ry-next --list
ry-next git --ry-help
```

### Key Features
- Clean architecture with single-responsibility components
- No backward compatibility - clean API design
- Type-safe recursive template processing
- Library system with metadata support

## ry-tool (Legacy)

The original implementation, still functional but being phased out.

- **Location**: `src/ry_tool/`
- **Documentation**: `README.md`, `VISION.md`, `EXAMPLES.md`
- **Libraries**: `libraries/` (legacy v1.0 format)

## Development Status

- **ry-next**: Active development, production-ready
- **ry-tool**: Maintenance mode, no new features

## Project Structure

```
ry-tool/
├── src/
│   ├── ry_next/         # Next generation (active)
│   └── ry_tool/         # Legacy version
├── docs_next/           # ry-next documentation
│   ├── ry-next/         # Main docs
│   ├── libraries/       # Production libraries
│   └── examples/        # Working examples
├── libraries/           # Legacy ry-tool libraries
├── docs/                # Legacy documentation
└── pyproject.toml       # Both tools installed
```

## Migration

To migrate from ry-tool to ry-next:
1. Libraries need rewriting in v2.0 format
2. Use `--ry-help` instead of `--help`
3. Direct class instantiation (no convenience wrappers)

See `docs_next/ry-next/README.md` for complete documentation.