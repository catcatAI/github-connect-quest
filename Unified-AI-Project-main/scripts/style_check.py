#!/usr/bin/env python3
"""
Unified AI Project - Custom Style Checker
統一AI專案 - 自定義風格檢查器

This script performs project-specific style and convention checks
beyond what standard linters provide.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any


class UnifiedAIStyleChecker:
    """Custom style checker for Unified AI Project."""
    
    def __init__(self):
        self.errors: List[Tuple[str, int, str]] = []
        self.warnings: List[Tuple[str, int, str]] = []
        
    def check_file(self, filepath: Path) -> None:
        """Check a single Python file for style violations."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._check_ast(filepath, tree)
            except SyntaxError as e:
                self.errors.append((str(filepath), e.lineno or 0, f"Syntax error: {e}"))
                return
                
            # Check content patterns
            self._check_content_patterns(filepath, content)
            
        except Exception as e:
            self.errors.append((str(filepath), 0, f"Failed to read file: {e}"))
    
    def _check_ast(self, filepath: Path, tree: ast.AST) -> None:
        """Check AST for structural violations."""
        for node in ast.walk(tree):
            # Check class naming conventions
            if isinstance(node, ast.ClassDef):
                self._check_class_naming(filepath, node)
                
            # Check function naming conventions
            elif isinstance(node, ast.FunctionDef):
                self._check_function_naming(filepath, node)
                
            # Check AI-specific patterns
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self._check_import_patterns(filepath, node)
    
    def _check_class_naming(self, filepath: Path, node: ast.ClassDef) -> None:
        """Check class naming conventions."""
        class_name = node.name
        
        # AI component classes should follow specific patterns
        if 'core_ai' in str(filepath):
            if class_name.endswith('Manager') and not re.match(r'^[A-Z][a-zA-Z]*Manager$', class_name):
                self.warnings.append((
                    str(filepath), 
                    node.lineno, 
                    f"AI Manager class '{class_name}' should follow pattern: XxxManager"
                ))
                
            if class_name.endswith('Engine') and not re.match(r'^[A-Z][a-zA-Z]*Engine$', class_name):
                self.warnings.append((
                    str(filepath), 
                    node.lineno, 
                    f"AI Engine class '{class_name}' should follow pattern: XxxEngine"
                ))
    
    def _check_function_naming(self, filepath: Path, node: ast.FunctionDef) -> None:
        """Check function naming conventions."""
        func_name = node.name
        
        # Check for AI-specific function patterns
        if 'core_ai' in str(filepath):
            # AI processing functions should be descriptive
            if len(func_name) < 3 and not func_name.startswith('_'):
                self.warnings.append((
                    str(filepath), 
                    node.lineno, 
                    f"AI function '{func_name}' should have descriptive name (>= 3 chars)"
                ))
    
    def _check_import_patterns(self, filepath: Path, node: ast.AST) -> None:
        """Check import patterns for AI components."""
        if isinstance(node, ast.ImportFrom):
            module = node.module
            if module and 'core_ai' in module:
                # Check for circular imports in AI components
                current_module = str(filepath).replace('/', '.').replace('.py', '')
                if module in current_module:
                    self.errors.append((
                        str(filepath), 
                        node.lineno, 
                        f"Potential circular import: {module}"
                    ))
    
    def _check_content_patterns(self, filepath: Path, content: str) -> None:
        """Check content for specific patterns."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME patterns
            if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                self.warnings.append((
                    str(filepath), 
                    i, 
                    f"Found development marker: {line.strip()}"
                ))
            
            # Check for hardcoded paths
            if re.search(r'["\'][A-Za-z]:[\\\/]', line) or re.search(r'["\']\/[a-zA-Z]', line):
                if 'test' not in str(filepath).lower():
                    self.warnings.append((
                        str(filepath), 
                        i, 
                        "Potential hardcoded path found"
                    ))
            
            # Check for print statements in non-test files
            if re.search(r'\bprint\s*\(', line) and 'test' not in str(filepath).lower():
                if 'debug' not in line.lower() and 'example' not in str(filepath).lower():
                    self.warnings.append((
                        str(filepath), 
                        i, 
                        "Consider using logging instead of print()"
                    ))
            
            # Check for AI-specific patterns
            if 'core_ai' in str(filepath):
                # AI components should have proper error handling
                if re.search(r'except\s*:', line):
                    self.warnings.append((
                        str(filepath), 
                        i, 
                        "AI components should use specific exception handling"
                    ))
    
    def check_directory(self, directory: Path) -> None:
        """Check all Python files in directory recursively."""
        for py_file in directory.rglob('*.py'):
            # Skip certain directories
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'build', 'dist']):
                continue
                
            self.check_file(py_file)
    
    def report(self) -> int:
        """Generate report and return exit code."""
        total_issues = len(self.errors) + len(self.warnings)
        
        if self.errors:
            print("🚨 ERRORS:")
            for filepath, lineno, message in self.errors:
                print(f"  {filepath}:{lineno} - {message}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for filepath, lineno, message in self.warnings:
                print(f"  {filepath}:{lineno} - {message}")
            print()
        
        if total_issues == 0:
            print("✅ No style issues found!")
            return 0
        else:
            print(f"📊 Found {len(self.errors)} errors and {len(self.warnings)} warnings")
            return 1 if self.errors else 0


def main():
    """Main entry point."""
    checker = UnifiedAIStyleChecker()
    
    # Check src directory
    src_dir = Path('src')
    if src_dir.exists():
        checker.check_directory(src_dir)
    else:
        print("❌ src/ directory not found")
        return 1
    
    return checker.report()


if __name__ == '__main__':
    sys.exit(main())