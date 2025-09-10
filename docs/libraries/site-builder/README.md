# site-builder

Static site generator that reads `project.yaml` manifests and generates beautiful documentation sites.

## Installation

```bash
ry-next ry-lib install site-builder
```

## Usage

### 1. Create project manifest

```bash
# Generate project.yaml from your project
ry-next ry-lib project init
```

### 2. Build site

```bash
# Generate static site in docs/
ry-next site-builder build
```

### 3. Preview

```bash
# Serve locally on http://localhost:8000
ry-next site-builder serve
```

### 4. Watch mode

```bash
# Auto-rebuild on changes
ry-next site-builder watch
```

## Commands

- `build` - Generate static site from project.yaml
- `serve` - Development server with live preview
- `watch` - Auto-rebuild on file changes
- `clean` - Remove generated files

## Features

- **Zero Configuration** - Just needs project.yaml
- **Multiple Themes** - terminal, minimal, cards
- **Auto-Discovery** - Finds libraries, packages, documentation
- **Search Support** - Client-side search with Lunr.js
- **Copy Buttons** - One-click code copying
- **Dark Mode** - Automatic theme switching
- **Responsive** - Mobile-friendly design

## Project Manifest

The site-builder reads `project.yaml` files with this structure:

```yaml
schema: "1.0"
project:
  name: my-project
  type: library-collection
  description: Project description
  version: 1.0.0

content:
  libraries:
    path: docs/libraries
    registry: docs/registry.json
  documentation:
    readme: README.md
    changelog: CHANGELOG.md

site:
  theme: terminal
  features:
    - search
    - copy-buttons
    - dark-mode
```

## Themes

### Terminal
Perfect for CLI tools and developer-focused projects. Features monospace fonts and terminal-style aesthetics.

### Minimal
Clean and simple design focusing on readability.

### Cards
Visual card-based layout for showcasing multiple libraries or packages.