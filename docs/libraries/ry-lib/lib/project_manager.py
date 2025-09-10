"""Project manifest management for ry-lib."""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import os

# Import from ry_tool directly (available in exec environment)
from ry_tool.utils import LibraryBase, FileManager, VersionManager


class ProjectManager(LibraryBase):
    """Manage project.yaml manifest files."""
    
    def __init__(self):
        super().__init__(base_path='docs/libraries')
        
    def init_project(self, force: bool = False) -> bool:
        """Initialize project.yaml from current directory."""
        project_file = Path('project.yaml')
        
        if project_file.exists() and not force:
            return False
        
        # Detect project info
        project_data = self._detect_project_info()
        
        # Write project.yaml
        self.file_manager.save_yaml(project_data, project_file)
        return True
    
    def sync_project(self) -> List[str]:
        """Sync project.yaml with source files."""
        changes = []
        project_file = Path('project.yaml')
        
        if not project_file.exists():
            raise FileNotFoundError("project.yaml not found. Run: ry ry-lib project init")
        
        project = self.file_manager.load_yaml(project_file)
        
        # Sync version from pyproject.toml
        if Path('pyproject.toml').exists():
            pyproject = self._load_pyproject()
            new_version = pyproject.get('project', {}).get('version')
            if new_version and new_version != project['project']['version']:
                old_version = project['project']['version']
                project['project']['version'] = new_version
                changes.append(f"Version: {old_version} → {new_version}")
        
        # Update library count
        if Path('docs/libraries').exists():
            libraries = self._scan_libraries()
            old_count = project.get('content', {}).get('libraries', {}).get('count', 0)
            if libraries != old_count:
                project.setdefault('content', {}).setdefault('libraries', {})['count'] = libraries
                changes.append(f"Libraries: {old_count} → {libraries}")
        
        # Update registry if exists
        if Path('docs/registry.json').exists():
            project.setdefault('content', {}).setdefault('libraries', {})['registry'] = 'docs/registry.json'
        
        if changes:
            self.file_manager.save_yaml(project, project_file)
        
        return changes
    
    def validate_project(self) -> Tuple[bool, List[str]]:
        """Validate project.yaml structure."""
        errors = []
        project_file = Path('project.yaml')
        
        if not project_file.exists():
            return False, ["project.yaml not found"]
        
        project = self.file_manager.load_yaml(project_file)
        
        # Check required fields
        required = ['schema', 'project']
        for field in required:
            if field not in project:
                errors.append(f"Missing required field: {field}")
        
        # Validate project section
        if 'project' in project:
            required_project = ['name', 'type', 'description']
            for field in required_project:
                if field not in project['project']:
                    errors.append(f"Missing project.{field}")
        
        # Validate type
        valid_types = ['package', 'application', 'library-collection', 'framework']
        if project.get('project', {}).get('type') not in valid_types:
            errors.append(f"Invalid project type. Must be one of: {valid_types}")
        
        return len(errors) == 0, errors
    
    def show_project(self) -> Dict[str, Any]:
        """Load and return project.yaml contents."""
        project_file = Path('project.yaml')
        if not project_file.exists():
            raise FileNotFoundError("project.yaml not found")
        
        return self.file_manager.load_yaml(project_file)
    
    def _detect_project_info(self) -> Dict[str, Any]:
        """Auto-detect project information."""
        info = {
            'schema': '1.0',
            'project': {
                'name': Path.cwd().name,
                'type': 'package',
                'description': 'Project description',
                'version': '0.1.0',
                'license': 'MIT'
            }
        }
        
        # From pyproject.toml
        if Path('pyproject.toml').exists():
            pyproject = self._load_pyproject()
            if 'project' in pyproject:
                proj = pyproject['project']
                info['project']['name'] = proj.get('name', info['project']['name'])
                info['project']['version'] = proj.get('version', '0.1.0')
                info['project']['description'] = proj.get('description', '')
                
                # Extract maintainers
                if 'authors' in proj:
                    info['maintainers'] = [
                        {'name': a.get('name', ''), 'email': a.get('email', '')}
                        for a in proj['authors']
                    ]
                
                # Detect installation methods
                info['installation'] = {
                    'primary': 'uv' if 'uv' in str(pyproject) else 'pip',
                    'methods': []
                }
                
                pkg_name = info['project']['name']
                # Check if it's a tool or library
                if 'project.scripts' in str(pyproject) or 'tool.uv.scripts' in str(pyproject):
                    info['installation']['methods'] = [
                        {'tool': 'uv', 'command': f"uv tool install {pkg_name}"},
                        {'tool': 'pipx', 'command': f"pipx install {pkg_name}"},
                        {'tool': 'pip', 'command': f"pip install {pkg_name}"}
                    ]
                else:
                    info['installation']['methods'] = [
                        {'tool': 'uv', 'command': f"uv add {pkg_name}"},
                        {'tool': 'pip', 'command': f"pip install {pkg_name}"}
                    ]
        
        # Detect repository from git
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                repo_url = result.stdout.strip()
                # Convert SSH to HTTPS
                if repo_url.startswith('git@github.com:'):
                    repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
                    repo_url = repo_url.replace('.git', '')
                
                info['source'] = {
                    'repository': repo_url,
                    'homepage': repo_url,  # Can be customized later
                    'issues': f"{repo_url}/issues"
                }
        except:
            pass
        
        # Detect content structure
        info['content'] = {}
        
        # Check for libraries
        if Path('docs/libraries').exists():
            info['project']['type'] = 'library-collection'
            lib_count = self._scan_libraries()
            info['content']['libraries'] = {
                'path': 'docs/libraries',
                'count': lib_count
            }
            if Path('docs/registry.json').exists():
                info['content']['libraries']['registry'] = 'docs/registry.json'
        
        # Documentation
        doc_section = {}
        if Path('README.md').exists():
            doc_section['readme'] = 'README.md'
        if Path('CHANGELOG.md').exists():
            doc_section['changelog'] = 'CHANGELOG.md'
        if Path('examples').exists():
            doc_section['examples'] = 'examples/'
        
        if doc_section:
            info['content']['documentation'] = doc_section
        
        # Package info
        if Path('pyproject.toml').exists():
            info['content']['package'] = {
                'manifest': 'pyproject.toml',
                'source': 'src/' if Path('src').exists() else None
            }
        
        # Default site preferences
        info['site'] = {
            'theme': 'terminal' if info['project']['type'] == 'library-collection' else 'minimal',
            'accent': '#00ff00',
            'features': ['search', 'copy-buttons', 'dark-mode']
        }
        
        return info
    
    def _load_pyproject(self) -> Dict[str, Any]:
        """Load pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                # Fallback: parse manually for basic fields
                content = Path('pyproject.toml').read_text()
                # Extract basic fields with regex
                import re
                
                result = {}
                # Get project section
                if '[project]' in content:
                    project = {}
                    # Extract name
                    match = re.search(r'name\s*=\s*"([^"]+)"', content)
                    if match:
                        project['name'] = match.group(1)
                    # Extract version
                    match = re.search(r'version\s*=\s*"([^"]+)"', content)
                    if match:
                        project['version'] = match.group(1)
                    # Extract description
                    match = re.search(r'description\s*=\s*"([^"]+)"', content)
                    if match:
                        project['description'] = match.group(1)
                    
                    if project:
                        result['project'] = project
                
                return result
        
        with open('pyproject.toml', 'rb') as f:
            return tomllib.load(f)
    
    def _scan_libraries(self) -> int:
        """Count libraries in docs/libraries."""
        lib_path = Path('docs/libraries')
        if not lib_path.exists():
            return 0
        
        count = 0
        for item in lib_path.iterdir():
            if item.is_dir() and (item / f"{item.name}.yaml").exists():
                count += 1
        
        return count