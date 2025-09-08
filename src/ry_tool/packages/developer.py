"""
Package developer tools for ry libraries (maintainer commands).
Handles creating, validating, and publishing libraries.
"""

import subprocess
import sys
from pathlib import Path

from .registry import Registry


class PackageDeveloper:
    """Developer tools for maintaining ry libraries."""

    def __init__(self):
        """Initialize package developer tools."""
        self.registry = Registry()
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.docs_dir = self.project_root / "docs"
        self.libraries_dir = self.project_root / "libraries"  # Libraries at root now

    def new(self, name: str) -> bool:
        """
        Create a new library template.

        Args:
            name: Library name

        Returns:
            True if successful, False otherwise
        """
        lib_dir = self.libraries_dir / name

        if lib_dir.exists():
            print(f"❌ Library '{name}' already exists!")
            return False

        print(f"📝 Creating new library: {name}")
        lib_dir.mkdir(parents=True)

        # Create main YAML file
        yaml_template = f"""# {name} library for ry
# Generated template - customize as needed

match:
  # Define your command patterns here
  test:
    - shell: echo "Running {name} test"
  
  default:
    - shell: echo "Usage: ry {name} [command]"
    - shell: echo "Available commands: test"
"""

        yaml_file = lib_dir / f"{name}.yaml"
        yaml_file.write_text(yaml_template)

        # Create meta.yaml
        meta_template = f"""# Metadata for {name} library
description: "{name} library for ry"
author: "unknown"
version: "0.1.0"
"""

        meta_file = lib_dir / "meta.yaml"
        meta_file.write_text(meta_template)

        # Create lib directory for helper scripts
        lib_subdir = lib_dir / "lib"
        lib_subdir.mkdir()

        # Create a README
        readme_template = f"""# {name}

A ry library for {name} operations.

## Installation

```bash
ry --install {name}
```

## Usage

```bash
ry {name} test
```

## Commands

- `test`: Run test command
"""

        readme_file = lib_dir / "README.md"
        readme_file.write_text(readme_template)

        print(f"✅ Created library template at {lib_dir}")
        print(f"   Edit: {yaml_file}")
        print(f"   Test: ry {yaml_file} test")
        return True

    def check(self) -> bool:
        """
        Validate all library YAML files.

        Returns:
            True if all valid, False otherwise
        """
        if not self.libraries_dir.exists():
            print("❌ No libraries directory found")
            return False

        print("🔍 Checking all libraries...")
        all_valid = True

        for lib_dir in self.libraries_dir.iterdir():
            if not lib_dir.is_dir():
                continue

            yaml_file = lib_dir / f"{lib_dir.name}.yaml"
            if not yaml_file.exists():
                print(f"  ❌ {lib_dir.name}: Missing {lib_dir.name}.yaml")
                all_valid = False
                continue

            # Try to parse the YAML
            try:
                import yaml

                with open(yaml_file) as f:
                    yaml.safe_load(f)
                print(f"  ✅ {lib_dir.name}: Valid")
            except Exception as e:
                print(f"  ❌ {lib_dir.name}: Invalid YAML - {e}")
                all_valid = False

        return all_valid

    def test(self, name: str, *args) -> bool:
        """
        Test a library locally.

        Args:
            name: Library name
            args: Additional arguments to pass

        Returns:
            True if successful, False otherwise
        """
        # First check in docs/libraries
        yaml_path = self.libraries_dir / name / f"{name}.yaml"

        # If not found, check if it's a path
        if not yaml_path.exists():
            yaml_path = Path(name)
            if not yaml_path.exists():
                print(f"❌ Library '{name}' not found")
                return False

        print(f"🧪 Testing {yaml_path}")

        # Run ry with the library
        cmd = [sys.executable, "-m", "ry_tool", str(yaml_path)] + list(args)
        result = subprocess.run(cmd)

        return result.returncode == 0

    def update_registry(self) -> bool:
        """
        Update the registry.json from libraries directory.

        Returns:
            True if successful, False otherwise
        """
        print("📋 Updating registry...")

        # Ensure docs directory exists
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # Scan and update
        registry = self.registry.update_registry()

        # Save
        self.registry.save_local(registry)

        lib_count = len(registry.get("libraries", {}))
        print(f"✅ Registry updated with {lib_count} libraries")
        print(f"   File: {self.registry.registry_file}")

        return True

    def publish(self) -> bool:
        """
        Update registry and push to git.

        Returns:
            True if successful, False otherwise
        """
        # First update registry
        if not self.update_registry():
            return False

        print("📤 Publishing changes...")

        # Git operations
        try:
            # Add changes
            subprocess.run(["git", "add", "docs/"], cwd=self.project_root, check=True)

            # Check if there are changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"], cwd=self.project_root
            )

            if result.returncode == 0:
                print("ℹ️  No changes to publish")
                return True

            # Commit
            subprocess.run(
                ["git", "commit", "-m", "chore: update library registry"],
                cwd=self.project_root,
                check=True,
            )

            # Push
            subprocess.run(["git", "push"], cwd=self.project_root, check=True)

            print("✅ Published to repository")
            print("   Registry will be available at:")
            print(f"   {self.registry.registry_url}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
