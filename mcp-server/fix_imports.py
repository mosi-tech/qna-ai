#!/usr/bin/env python3
"""
Fix all relative import issues in analytics modules.

This script systematically replaces all relative imports with proper absolute imports
by adding the analytics root directory to sys.path and using absolute import paths.
"""

import os
import re
import glob

def fix_imports_in_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Get the relative depth (how many .. to go up to analytics root)
    rel_path = os.path.relpath(filepath, '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server/analytics')
    depth = len([p for p in rel_path.split('/') if p and p != '.']) - 1
    
    # Pattern to match relative imports
    relative_import_pattern = r'from \.\.+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*) import'
    
    def replace_relative_import(match):
        import_path = match.group(1)
        # Remove leading dots and convert to absolute path
        return f'from {import_path} import'
    
    # Check if file already has the path setup
    has_path_setup = 'analytics_root' in content and 'sys.path.insert' in content
    
    # Find all relative imports
    relative_imports = re.findall(relative_import_pattern, content)
    
    if relative_imports and not has_path_setup:
        # Add path setup at the top of imports section
        import_section_start = content.find('import ')
        if import_section_start != -1:
            # Find the position after the docstring and before first import
            lines = content.split('\n')
            insert_pos = 0
            in_docstring = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if in_docstring:
                        in_docstring = False
                        insert_pos = i + 1
                    else:
                        in_docstring = True
                elif not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
                    insert_pos = i
                    break
            
            # Insert path setup
            path_setup = [
                '',
                '# Add analytics root to path for absolute imports',
                'import sys',
                'import os',
                'analytics_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
                'if analytics_root not in sys.path:',
                '    sys.path.insert(0, analytics_root)',
                ''
            ]
            
            lines = lines[:insert_pos] + path_setup + lines[insert_pos:]
            content = '\n'.join(lines)
    
    # Replace relative imports
    content = re.sub(relative_import_pattern, replace_relative_import, content)
    
    # Handle inline relative imports (inside functions)
    inline_pattern = r'(\s+)from \.\.+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*) import'
    content = re.sub(inline_pattern, r'\1from \2 import', content)
    
    if content != original_content:
        print(f"Fixed imports in: {filepath}")
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fix all import issues in analytics modules"""
    print("🔧 Fixing all relative import issues in analytics modules...")
    
    analytics_dir = '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server/analytics'
    
    # Find all Python files
    py_files = []
    for root, dirs, files in os.walk(analytics_dir):
        # Skip test directories
        if 'tests' in root:
            continue
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                py_files.append(os.path.join(root, file))
    
    print(f"Found {len(py_files)} Python files to process...")
    
    fixed_count = 0
    for filepath in py_files:
        if fix_imports_in_file(filepath):
            fixed_count += 1
    
    print(f"\n✅ Fixed imports in {fixed_count} files!")
    
    # Test imports
    print("\n🧪 Testing imports...")
    import sys
    sys.path.insert(0, analytics_dir)
    
    test_modules = [
        'utils.data_utils',
        'performance.metrics', 
        'portfolio.metrics',
        'risk.metrics'
    ]
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} imports successfully")
        except Exception as e:
            print(f"❌ {module} import failed: {e}")
    
    print("\n🎉 Import fixing completed!")

if __name__ == '__main__':
    main()