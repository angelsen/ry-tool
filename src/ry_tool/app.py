"""
Main CLI application for ry using the mini framework.
"""

from pathlib import Path

from ._cli import CLI
from .core import RY
from .packages import PackageManager, LibraryResolver


# Create the CLI app
app = CLI(name="ry", description="YAML command orchestrator with package management")


# Package management commands
@app.command(
    "--install",
    help="Install a library from registry",
    requires_arg=True,
    arg_name="library",
)
def install(library: str):
    """Install a library from the registry."""
    manager = PackageManager()
    return manager.install(library)


@app.command("--update", help="Update library (or all if none specified)")
def update(library: str = None):
    """Update installed libraries."""
    manager = PackageManager()
    if library:
        return manager.update(library)
    return manager.update()


@app.command(
    "--uninstall",
    help="Remove an installed library",
    requires_arg=True,
    arg_name="library",
)
def uninstall(library: str):
    """Uninstall a library."""
    manager = PackageManager()
    return manager.uninstall(library)


@app.command("--list", help="List installed libraries")
def list_libraries():
    """List installed libraries."""
    manager = PackageManager()
    libraries = manager.list_installed()
    if libraries:
        print("📦 Installed libraries:")
        for lib in libraries:
            status = "✓" if lib["exists"] else "✗"
            version = lib["version"] if lib["version"] != "unknown" else ""
            version_str = f"@{version}" if version else ""
            print(f"  {status} {lib['name']}{version_str}")
    else:
        print("No libraries installed")
    return True


@app.command("--search", help="Search available libraries")
def search(query: str = ""):
    """Search the registry."""
    manager = PackageManager()
    results = manager.search(query)
    if results:
        print("🔍 Available libraries:")
        for lib in results:
            version = lib.get("version", "")
            version_str = f"@{version}" if version and version != "unknown" else ""
            desc = lib.get("description", "")
            desc_str = f" - {desc}" if desc else ""
            print(f"  • {lib['name']}{version_str}{desc_str}")
    else:
        print("No libraries found")
    return True


# Default handler for library execution
@app.default
def execute_library(first_arg: str, *args):
    """Execute a library or YAML file."""
    # Resolve library to YAML path
    if Path(first_arg).suffix == ".yaml":
        # Direct YAML file
        config_path = Path(first_arg)
        if not config_path.exists():
            raise FileNotFoundError(f"File not found: {first_arg}")
        remaining_args = args
    else:
        # Try to resolve as library name
        resolver = LibraryResolver()
        result = resolver.resolve(first_arg, list(args))

        if result:
            config_path, remaining_args = result
        else:
            print(f"Library '{first_arg}' not found")
            print(f"Try: ry --install {first_arg}")
            return False

    # Execute the library/YAML file
    ry = RY(config_path, remaining_args)
    return ry.run()


def run():
    """Entry point for the CLI."""
    app.run()
