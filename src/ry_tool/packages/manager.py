"""
Package manager for ry libraries (user commands).
Handles installation, updates, and listing of libraries.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .registry import Registry


class PackageManager:
    """Manages library installation and updates for users."""

    def __init__(self):
        """Initialize package manager."""
        # Use XDG_DATA_HOME or fallback
        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")
        self.base_dir = Path(xdg_data) / "ry"
        self.libraries_dir = self.base_dir / "libraries"
        self.installed_file = self.base_dir / "installed.json"

        # Ensure directories exist
        self.libraries_dir.mkdir(parents=True, exist_ok=True)

        # Registry instance
        self.registry = Registry()

        # Load installed libraries tracking
        self.installed = self._load_installed()

    def _load_installed(self) -> Dict:
        """Load the installed libraries tracking file."""
        if self.installed_file.exists():
            with open(self.installed_file) as f:
                return json.load(f)
        return {}

    def _save_installed(self):
        """Save the installed libraries tracking file."""
        with open(self.installed_file, "w") as f:
            json.dump(self.installed, f, indent=2)

    def _check_version_requirement(self, installed_version: str, requirement: str) -> bool:
        """Check if installed version satisfies requirement."""
        # Simple version checking for now (can enhance later)
        if requirement.startswith(">="):
            required = requirement[2:].strip()
            return installed_version >= required
        elif requirement.startswith(">"):
            required = requirement[1:].strip()
            return installed_version > required
        else:
            # Exact version or no operator means >=
            required = requirement.strip()
            return installed_version >= required

    def install(self, name: str, is_dependency: bool = False) -> bool:
        """
        Install a library from the registry with dependency resolution.

        Args:
            name: Library name to install
            is_dependency: Whether this is being installed as a dependency

        Returns:
            True if successful, False otherwise
        """
        indent = "  " if is_dependency else ""
        print(f"{indent}📦 Installing {name}...")

        # Get registry (remote or local)
        registry = self.registry.get_registry()
        if not registry or not registry.get("libraries"):
            print(f"{indent}❌ No registry available")
            return False

        # Check if library exists
        if name not in registry.get("libraries", {}):
            print(f"{indent}❌ Library '{name}' not found in registry")
            if not is_dependency:
                print(f"   Try: ry --search {name}")
            return False

        lib_info = registry["libraries"][name]
        base_url = registry.get("base_url", self.registry.libraries_url)
        
        # Check if already installed with sufficient version
        if name in self.installed:
            installed_version = self.installed[name].get("version", "0.0.0")
            if not is_dependency:
                # For direct installs, always update
                print(f"{indent}⚠️  Updating existing installation...")
            else:
                # For dependencies, check if version is sufficient
                print(f"{indent}✓ {name} already installed (v{installed_version})")
                return True
        
        # Install dependencies first
        if "dependencies" in lib_info:
            print(f"{indent}📎 Checking dependencies for {name}...")
            for dep_name, dep_version in lib_info.get("dependencies", {}).items():
                # Check if dependency is installed and meets version requirement
                if dep_name in self.installed:
                    installed_version = self.installed[dep_name].get("version", "0.0.0")
                    if self._check_version_requirement(installed_version, dep_version):
                        print(f"{indent}  ✓ {dep_name} {dep_version} satisfied")
                        continue
                
                # Need to install/update dependency
                print(f"{indent}  → Installing dependency: {dep_name} {dep_version}")
                if not self.install(dep_name, is_dependency=True):
                    print(f"{indent}❌ Failed to install dependency: {dep_name}")
                    return False

        # Create library directory
        lib_dir = self.libraries_dir / name
        if lib_dir.exists():
            print("⚠️  Removing existing installation...")
            shutil.rmtree(lib_dir)
        lib_dir.mkdir(parents=True)

        # Check if we can copy from local development libraries (now in docs)
        local_source = self.registry.libraries_dir / name
        if local_source.exists() and local_source.is_dir():
            # Copy from local development
            print(f"  📂 Copying from local: {local_source}")
            try:
                shutil.copytree(local_source, lib_dir, dirs_exist_ok=True)
                success = True
            except Exception as e:
                print(f"  ❌ Failed to copy: {e}")
                success = False
        else:
            # Download each file from URL
            success = True
            for file_path in lib_info.get("files", []):
                file_url = f"{base_url}/{name}/{file_path}"
                local_file = lib_dir / file_path

                # Create subdirectories if needed
                local_file.parent.mkdir(parents=True, exist_ok=True)

                print(f"  ↓ {file_path}")
                try:
                    from ..config import config

                    subprocess.run(
                        [config.CURL, "-fsL", file_url, "-o", str(local_file)],
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError:
                    print(f"  ❌ Failed to download {file_path}")
                    success = False
                    break

        if success:
            # Update installed tracking
            self.installed[name] = {
                "version": lib_info.get("version", "unknown"),
                "files": lib_info.get("files", []),
            }
            self._save_installed()
            print(f"✅ Installed {name}")
            return True
        else:
            # Clean up on failure
            if lib_dir.exists():
                shutil.rmtree(lib_dir)
            return False

    def update(self, name: Optional[str] = None) -> bool:
        """
        Update library/libraries to latest version.

        Args:
            name: Specific library to update, or None for all

        Returns:
            True if successful, False otherwise
        """
        if name:
            # Update specific library
            if name not in self.installed:
                print(f"❌ Library '{name}' is not installed")
                return False
            print(f"🔄 Updating {name}...")
            return self.install(name)
        else:
            # Update all libraries
            print("🔄 Updating all libraries...")
            success = True
            for lib_name in self.installed.keys():
                if not self.install(lib_name):
                    success = False
            return success

    def uninstall(self, name: str) -> bool:
        """
        Uninstall a library.

        Args:
            name: Library name to uninstall

        Returns:
            True if successful, False otherwise
        """
        if name not in self.installed:
            print(f"❌ Library '{name}' is not installed")
            return False

        lib_dir = self.libraries_dir / name
        if lib_dir.exists():
            shutil.rmtree(lib_dir)

        del self.installed[name]
        self._save_installed()

        print(f"✅ Uninstalled {name}")
        return True

    def list_installed(self) -> List[Dict]:
        """
        List installed libraries.

        Returns:
            List of installed library info
        """
        libraries = []
        for name, info in self.installed.items():
            lib_dir = self.libraries_dir / name
            libraries.append(
                {
                    "name": name,
                    "version": info.get("version", "unknown"),
                    "path": str(lib_dir),
                    "exists": lib_dir.exists(),
                }
            )
        return libraries

    def search(self, query: str = "") -> List[Dict]:
        """
        Search for libraries in the registry.

        Args:
            query: Search term

        Returns:
            List of matching libraries
        """
        return self.registry.search(query)
