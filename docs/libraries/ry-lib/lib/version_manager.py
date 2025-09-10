#!/usr/bin/env python3
"""Version management for ry-next libraries."""

from pathlib import Path
from ry_tool.utils import LibraryBase, CommandBuilder


class LibraryVersionManager(LibraryBase):
    """Handle version management with shared utilities."""
    
    def bump_version(self, library: str, bump_type: str = 'patch', message: str = '') -> bool:
        """
        Bump library version.
        
        Args:
            library: Library name
            bump_type: Type of bump (major, minor, patch)
            message: Optional changelog message
        
        Returns:
            True if successful, False otherwise
        """
        if not self.library_exists(library):
            self.error_message(f"Library {library} not found")
            return False
    
        try:
            # Load current metadata
            meta = self.load_library_meta(library)
            if not meta:
                self.error_message(f"Could not load metadata for {library}")
                return False
            
            # Bump version
            old_version = meta.get('version', '0.0.0')
            new_version = self.version_manager.bump_version(old_version, bump_type)
            meta['version'] = new_version
            
            # Save updated metadata
            self.save_library_meta(library, meta)
        
            # Update CHANGELOG if it exists and message provided
            changelog_file = self.get_library_dir(library) / 'CHANGELOG.md'
            if changelog_file.exists() and message:
                self._update_changelog(changelog_file, new_version, message)
        
            print(f"📦 {library}: {old_version} → {new_version}")
            if message:
                print(f"   {message}")
            
            return True
        
        except Exception as e:
            self.error_message(f"Failed to bump version: {e}")
            return False


    def _update_changelog(self, changelog_file: Path, version: str, message: str):
        """Update CHANGELOG.md with new version entry."""
        from datetime import date
        
        with open(changelog_file) as f:
            content = f.read()
        
        # Find where to insert new version
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('## '):
                insert_idx = i
                break
        
        # Create new entry
        new_entry = f"\n## [{version}] - {date.today()}\n\n### Changed\n- {message}\n"
        lines.insert(insert_idx, new_entry)
        
        with open(changelog_file, 'w') as f:
            f.write('\n'.join(lines))


    def check_version_changes(self) -> bool:
        """
        Check if changed libraries have version bumps.
        Used for git pre-commit hooks.
        
        Returns:
            True if all changed libraries have version bumps, False otherwise
        """
    
        try:
            # Get changed files
            result = CommandBuilder(capture_output=True, text=True, check=True).run_git('diff', '--cached', '--name-only')
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception:
            print("Not in a git repository")
            return True
    
        # Check which libraries have changes
        changed_libs = set()
        for file in changed_files:
            if file.startswith('docs_next/libraries/'):
                parts = file.split('/')
                if len(parts) > 2:
                    changed_libs.add(parts[2])
        
        if not changed_libs:
            return True
    
        # Check if versions were bumped
        needs_bump = []
        for lib in changed_libs:
            if self.get_meta_yaml(lib).exists():
                # Check if meta.yaml itself was changed
                meta_path = f'docs_next/libraries/{lib}/meta.yaml'
                if meta_path not in changed_files:
                    needs_bump.append(lib)
        
        if needs_bump:
            self.error_message("Libraries changed without version bump:")
            for lib in needs_bump:
                print(f"   - {lib}")
            print("\nRun: ry-next ry-lib bump <library> --type patch")
            return False
        
        self.success_message("All changed libraries have version updates")
        return True



# Direct usage: manager = LibraryVersionManager(); manager.bump_version(lib, type, msg)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: version_manager.py <library> [type] [message]")
        print("       version_manager.py --check")
        sys.exit(1)
    
    manager = LibraryVersionManager()
    if sys.argv[1] == '--check':
        success = manager.check_version_changes()
    else:
        library = sys.argv[1]
        bump_type = sys.argv[2] if len(sys.argv) > 2 else 'patch'
        message = sys.argv[3] if len(sys.argv) > 3 else ''
        success = manager.bump_version(library, bump_type, message)
    
    sys.exit(0 if success else 1)