#!/usr/bin/env python3
"""
Static site builder for project registries.
Generates index.html from registry.json/packages.json and site.yaml.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
import sys


def load_config():
    """Load site.yaml configuration."""
    config_path = Path("site.yaml")
    if not config_path.exists():
        print("ERROR: site.yaml not found", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_registry(registry_path):
    """Load registry or packages JSON."""
    path = Path(registry_path)
    if not path.exists():
        print(f"WARNING: {registry_path} not found", file=sys.stderr)
        return {}
    
    with open(path) as f:
        return json.load(f)


def render_setup_commands(setup_items):
    """Render installation commands with tabs."""
    if not setup_items:
        return ""
    
    # Create tab buttons
    tabs = []
    contents = []
    
    for i, item in enumerate(setup_items):
        active = "active" if item.get("default") else ""
        tabs.append(f'<button class="tab-button {active}" data-tab="{i}">{item["name"]}</button>')
        
        display = "block" if item.get("default") else "none"
        contents.append(f'''
        <div class="tab-content" id="tab-{i}" style="display: {display};">
            <div style="position: relative;">
                <pre id="setup-{i}"><code>{item["command"]}</code></pre>
                <button class="copy-btn" onclick="copyCode('setup-{i}', this)">Copy</button>
            </div>
        </div>
        ''')
    
    return f'''
    <div class="tabs">
        <div class="tab-buttons">
            {" ".join(tabs)}
        </div>
        {"".join(contents)}
    </div>
    '''


def render_items(registry, item_type):
    """Render packages or libraries."""
    items_html = []
    
    # Handle different registry formats
    if "packages" in registry:  # arch-repo style
        items = registry["packages"]
        for item in items:
            items_html.append(render_package(item))
    elif "libraries" in registry:  # ry-tool style
        items = registry["libraries"]
        for name, info in items.items():
            info["name"] = name
            items_html.append(render_library(info))
    else:
        return '<div class="item"><p>No items found in registry.</p></div>'
    
    return "\n".join(items_html)


def render_package(pkg):
    """Render a package (arch-repo style)."""
    homepage = f'<p><a href="{pkg["url"]}" target="_blank">Homepage ↗</a></p>' if pkg.get("url") else ""
    return f'''
    <div class="item">
        <h3>{pkg["name"]}</h3>
        <p>{pkg.get("description", "No description")}</p>
        <p>Version: {pkg.get("version", "unknown")}</p>
        {homepage}
        <div style="position: relative;">
            <pre class="install-cmd" id="cmd-{pkg["name"]}">ap install {pkg["name"]}</pre>
            <button class="copy-btn" onclick="copyCode('cmd-{pkg["name"]}', this)">Copy</button>
        </div>
    </div>
    '''


def render_library(lib):
    """Render a library (ry-tool style)."""
    version = f'@{lib["version"]}' if lib.get("version") and lib["version"] != "unknown" else ""
    author = f'<p>Author: {lib["author"]}</p>' if lib.get("author") else ""
    return f'''
    <div class="item">
        <h3>{lib["name"]}{version}</h3>
        <p>{lib.get("description", "No description")}</p>
        {author}
        <div style="position: relative;">
            <pre class="install-cmd" id="cmd-{lib["name"]}">ry --install {lib["name"]}</pre>
            <button class="copy-btn" onclick="copyCode('cmd-{lib["name"]}', this)">Copy</button>
        </div>
    </div>
    '''


def generate_html(config, registry):
    """Generate the complete HTML page."""
    
    # Determine item type
    item_type = config.get("item_type", "library")
    # Fix plural form: library -> libraries, package -> packages
    if item_type == "library":
        item_type_plural = "libraries"
    else:
        item_type_plural = item_type + "s"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config["title"]}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html {{
            height: 100%;
            background: #1e1e2e;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 2rem 3rem;
            background: #1e1e2e;
            color: #cdd6f4;
            min-height: 100vh;
            max-width: 900px;
        }}
        h1 {{
            color: #89b4fa;
            margin-bottom: 0.5rem;
        }}
        h2 {{
            color: #94e2d5;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        pre {{
            background: #181825;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #313244;
            position: relative;
        }}
        .copy-btn {{
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.25rem 0.5rem;
            background: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .copy-btn:hover {{
            background: #45475a;
            color: #a6e3a1;
        }}
        .copy-btn.copied {{
            background: #a6e3a1;
            color: #181825;
        }}
        code {{
            background: #181825;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            color: #f38ba8;
        }}
        .item {{
            background: #181825;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 8px;
            border: 1px solid #313244;
        }}
        .item h3 {{
            margin: 0 0 0.75rem 0;
            color: #a6e3a1;
            font-size: 1.3rem;
        }}
        .item p {{
            margin: 0.5rem 0;
            line-height: 1.5;
        }}
        .item pre {{
            margin-top: 1rem;
        }}
        a {{
            color: #89b4fa;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .install-cmd {{
            color: #a6e3a1;
        }}
        .tabs {{
            margin: 1rem 0;
        }}
        .tab-buttons {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        .tab-button {{
            padding: 0.5rem 1rem;
            background: #181825;
            color: #cdd6f4;
            border: 1px solid #313244;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .tab-button:hover {{
            background: #313244;
        }}
        .tab-button.active {{
            background: #313244;
            color: #89b4fa;
            border-color: #89b4fa;
        }}
        .tab-content {{
            display: none;
        }}
        .description {{
            color: #a6adc8;
            margin-bottom: 1rem;
        }}
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #313244;
            text-align: center;
            color: #6c7086;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>{config.get("icon", "📦")} {config["title"]}</h1>
    <p class="description">{config.get("description", "")}</p>

    <h2>⚡ Quick Setup</h2>
    {render_setup_commands(config.get("setup", []))}

    <h2>📋 Available {item_type_plural.title()}</h2>
    <div id="items-container">
        {render_items(registry, item_type)}
    </div>

    <h2>🔗 Links</h2>
    <div class="item">
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 0.5rem 0;">
                <a href="{config.get("repo", "#")}">GitHub Repository</a>
            </li>
            <li style="padding: 0.5rem 0;">
                <a href="{config.get("registry", "registry.json")}">Registry (JSON)</a>
            </li>
        </ul>
    </div>

    <div class="footer">
        <p>Generated by <a href="https://github.com/angelsen/ry-tool">ry site-builder</a> • {datetime.now().strftime("%Y-%m-%d")}</p>
    </div>

    <script>
        // Copy code functionality
        function copyCode(elementId, button) {{
            const codeElement = document.getElementById(elementId);
            const textToCopy = codeElement.textContent || codeElement.innerText;
            
            navigator.clipboard.writeText(textToCopy).then(() => {{
                button.textContent = 'Copied!';
                button.classList.add('copied');
                setTimeout(() => {{
                    button.textContent = 'Copy';
                    button.classList.remove('copied');
                }}, 2000);
            }}).catch(err => {{
                console.error('Failed to copy:', err);
                button.textContent = 'Failed';
                setTimeout(() => {{
                    button.textContent = 'Copy';
                }}, 2000);
            }});
        }}
        
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {{
            button.addEventListener('click', () => {{
                // Hide all contents
                document.querySelectorAll('.tab-content').forEach(content => {{
                    content.style.display = 'none';
                }});
                // Remove active class
                document.querySelectorAll('.tab-button').forEach(btn => {{
                    btn.classList.remove('active');
                }});
                // Show selected
                const tabId = button.getAttribute('data-tab');
                document.getElementById('tab-' + tabId).style.display = 'block';
                button.classList.add('active');
            }});
        }});
    </script>
</body>
</html>
'''
    return html


def main():
    """Main build function."""
    # Load configuration
    config = load_config()
    
    # Load registry
    registry_path = config.get("registry", "registry.json")
    registry = load_registry(registry_path)
    
    # Generate HTML
    html = generate_html(config, registry)
    
    # Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Write HTML file
    output_path = docs_dir / "index.html"
    output_path.write_text(html)
    
    print(f"Generated: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()