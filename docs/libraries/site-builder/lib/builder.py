"""Simplified site builder."""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Import from ry_tool directly (available in exec environment)
from ry_tool.utils import LibraryBase


class SiteBuilder(LibraryBase):
    """Static site builder from project.yaml."""
    
    def __init__(self):
        super().__init__(base_path='docs/libraries')
        self.template_path = Path(__file__).parent / 'templates' / 'base.html'
    
    def build(self, config_path: str = 'project.yaml', output_dir: str = 'docs', theme: str = 'minimal') -> None:
        """Build site from project.yaml."""
        # Load project manifest
        project = self.file_manager.load_yaml(Path(config_path))
        if not project:
            raise ValueError(f"Cannot load {config_path}")
        
        # Load template
        template = self.template_path.read_text()
        
        # Build context
        context = {
            'TITLE': project['project'].get('name', 'Documentation'),
            'DESCRIPTION': project['project'].get('description', ''),
            'THEME_CLASS': theme if theme in ['terminal', 'minimal'] else '',
            'HEADER': self._build_header(project['project']),
            'NAVIGATION': self._build_nav(project),
            'INSTALLATION': self._build_installation(project.get('installation', {})),
            'CONTENT': self._build_content(project),
            'FOOTER': self._build_footer(project)
        }
        
        # Replace markers
        html = template
        for marker, value in context.items():
            html = html.replace(f'<!-- {marker} -->', str(value))
        
        # Write output
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / 'index.html').write_text(html)
    
    def _build_header(self, project: Dict[str, Any]) -> str:
        """Build header HTML."""
        html = []
        html.append(f'<h1>{project.get("name", "Documentation")}</h1>')
        if 'description' in project:
            html.append(f'<p class="description">{project["description"]}</p>')
        if 'version' in project:
            html.append(f'<span class="version">v{project["version"]}</span>')
        return '\n'.join(html)
    
    def _build_nav(self, project: Dict[str, Any]) -> str:
        """Build navigation."""
        sections = []
        
        # Check what content exists
        if project.get('content', {}).get('libraries'):
            sections.append('<li><a href="#libraries">Libraries</a></li>')
        if project.get('content', {}).get('documentation'):
            sections.append('<li><a href="#documentation">Documentation</a></li>')
        if project.get('source', {}).get('repository'):
            sections.append(f'<li><a href="{project["source"]["repository"]}">GitHub</a></li>')
        
        if sections:
            return f'<ul>{" ".join(sections)}</ul>'
        return ''
    
    def _build_installation(self, installation: Dict[str, Any]) -> str:
        """Build installation section."""
        if not installation or 'methods' not in installation:
            return ''
        
        html = ['<section class="installation">']
        html.append('<h2>Installation</h2>')
        
        # Tab buttons
        html.append('<div class="tab-buttons">')
        for i, method in enumerate(installation['methods']):
            active = 'active' if i == 0 else ''
            html.append(f'<button class="tab-btn {active}" data-tab="install-{i}">{method["tool"]}</button>')
        html.append('</div>')
        
        # Tab content
        for i, method in enumerate(installation['methods']):
            active = 'active' if i == 0 else ''
            html.append(f'<div class="tab-content {active}" id="install-{i}">')
            html.append(f'<pre><code>{method["command"]}</code></pre>')
            html.append('</div>')
        
        html.append('</section>')
        return '\n'.join(html)
    
    def _build_content(self, project: Dict[str, Any]) -> str:
        """Build main content."""
        html = []
        
        # Libraries section
        if project.get('content', {}).get('libraries'):
            html.append(self._build_libraries(project['content']['libraries']))
        
        # Documentation section
        if project.get('content', {}).get('documentation'):
            html.append(self._build_documentation(project['content']['documentation']))
        
        return '\n'.join(html)
    
    def _build_libraries(self, lib_config: Dict[str, Any]) -> str:
        """Build libraries section."""
        lib_path = Path(lib_config['path'])
        if not lib_path.exists():
            return ''
        
        html = ['<section id="libraries">']
        html.append('<h2>Libraries</h2>')
        html.append('<div class="library-grid">')
        
        # Scan for libraries
        for lib_dir in sorted(lib_path.iterdir()):
            if not lib_dir.is_dir():
                continue
            
            lib_yaml = lib_dir / f"{lib_dir.name}.yaml"
            if not lib_yaml.exists():
                continue
            
            lib_data = self.file_manager.load_yaml(lib_yaml)
            if not lib_data:
                continue
            
            # Get metadata
            meta_yaml = lib_dir / "meta.yaml"
            version = None
            if meta_yaml.exists():
                meta = self.file_manager.load_yaml(meta_yaml)
                if meta:
                    version = meta.get('version')
            
            # Build card
            html.append('<div class="library-card">')
            if version:
                html.append(f'<span class="version">{version}</span>')
            html.append(f'<h3>{lib_data.get("name", lib_dir.name)}</h3>')
            html.append(f'<p>{lib_data.get("description", "")}</p>')
            
            # Show commands
            commands = list(lib_data.get('commands', {}).keys())
            if commands:
                html.append('<div class="commands">')
                for cmd in commands[:5]:
                    html.append(f'<span class="command">{cmd}</span>')
                if len(commands) > 5:
                    html.append(f'<span class="command">+{len(commands)-5} more</span>')
                html.append('</div>')
            
            html.append('</div>')
        
        html.append('</div>')
        html.append('</section>')
        return '\n'.join(html)
    
    def _build_documentation(self, doc_config: Dict[str, Any]) -> str:
        """Build documentation section."""
        html = ['<section id="documentation">']
        html.append('<h2>Documentation</h2>')
        
        # Add README content
        if 'readme' in doc_config:
            readme_path = Path(doc_config['readme'])
            if readme_path.exists():
                content = readme_path.read_text()
                # Simple markdown to HTML (just paragraphs and code blocks)
                content = self._simple_markdown(content)
                html.append(content)
        
        html.append('</section>')
        return '\n'.join(html)
    
    def _simple_markdown(self, text: str) -> str:
        """Very simple markdown processing."""
        lines = text.split('\n')
        html = []
        in_code = False
        
        for line in lines:
            if line.startswith('```'):
                if in_code:
                    html.append('</code></pre>')
                    in_code = False
                else:
                    html.append('<pre><code>')
                    in_code = True
            elif in_code:
                html.append(line)
            elif line.startswith('# '):
                # Skip h1 as we already have title
                continue
            elif line.startswith('## '):
                html.append(f'<h3>{line[3:]}</h3>')
            elif line.startswith('### '):
                html.append(f'<h4>{line[4:]}</h4>')
            elif line.strip():
                # Convert inline code
                line = line.replace('`', '<code>', 1).replace('`', '</code>', 1)
                html.append(f'<p>{line}</p>')
        
        return '\n'.join(html)
    
    def _build_footer(self, project: Dict[str, Any]) -> str:
        """Build footer."""
        html = []
        
        if 'repository' in project.get('source', {}):
            html.append(f'<a href="{project["source"]["repository"]}">View on GitHub</a> | ')
        
        html.append('Generated with ry site-builder')
        
        return ''.join(html)