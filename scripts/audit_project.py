#!/usr/bin/env python3
"""
Project Audit Script for Manalytics
Generates comprehensive PROJECT_AUDIT.json
"""
import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import re

class ProjectAuditor:
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.audit_data = {
            "metadata": {
                "audit_date": datetime.now().isoformat(),
                "project_root": str(self.root.absolute()),
                "version": "1.0.0"
            },
            "statistics": {},
            "files": {},
            "dependencies": {},
            "security_issues": [],
            "duplicates": [],
            "structure_analysis": {}
        }
        
    def run_full_audit(self):
        """Execute complete project audit"""
        print("🔍 Starting Manalytics Project Audit...")
        
        # 1. Scan all files
        self._scan_files()
        
        # 2. Analyze Python files
        self._analyze_python_files()
        
        # 3. Find security issues
        self._scan_security_issues()
        
        # 4. Detect duplicates
        self._find_duplicates()
        
        # 5. Analyze project structure
        self._analyze_structure()
        
        # 6. Generate statistics
        self._generate_statistics()
        
        # Save audit
        self._save_audit()
        
        print("✅ Audit complete! See PROJECT_AUDIT.json")
        
    def _scan_files(self):
        """Scan all project files"""
        print("📂 Scanning files...")
        
        exclude_dirs = {'.git', '__pycache__', 'venv', 'env', 'obsolete', '.pytest_cache'}
        file_types = {'.py', '.json', '.md', '.yml', '.yaml', '.txt', '.sql', '.sh'}
        
        for path in self.root.rglob('*'):
            try:
                if path.is_file() and not any(exc in str(path) for exc in exclude_dirs):
                    rel_path = str(path.relative_to(self.root))
                    
                    file_info = {
                        "size": path.stat().st_size,
                        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                        "extension": path.suffix,
                        "hash": self._get_file_hash(path)
                    }
                    
                    # Check for sensitive data
                    if path.suffix in ['.json', '.env', '.yml', '.yaml']:
                        file_info["potentially_sensitive"] = True
                        
                    self.audit_data["files"][rel_path] = file_info
            except PermissionError:
                # Skip files we can't access
                continue
            except Exception as e:
                print(f"⚠️ Error scanning {path}: {e}")
                continue
                
    def _analyze_python_files(self):
        """Analyze Python files for imports and structure"""
        print("🐍 Analyzing Python files...")
        
        python_files = [f for f in self.audit_data["files"] if f.endswith('.py')]
        
        for file_path in python_files:
            full_path = self.root / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract imports
                imports = self._extract_imports(content)
                self.audit_data["files"][file_path]["imports"] = imports
                
                # Check for classes and functions
                tree = ast.parse(content)
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                
                self.audit_data["files"][file_path]["classes"] = classes
                self.audit_data["files"][file_path]["functions"] = functions
                
            except Exception as e:
                self.audit_data["files"][file_path]["parse_error"] = str(e)
                
    def _extract_imports(self, content: str) -> List[str]:
        """Extract all imports from Python code"""
        imports = []
        
        # Simple import pattern
        import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(.+)$'
        
        for line in content.split('\n'):
            line = line.strip()
            if match := re.match(import_pattern, line):
                if match.group(1):  # from X import Y
                    imports.append(match.group(1))
                else:  # import X
                    imports.extend([imp.strip() for imp in match.group(2).split(',')])
                    
        return list(set(imports))
        
    def _scan_security_issues(self):
        """Scan for potential security issues"""
        print("🔒 Scanning for security issues...")
        
        # Patterns to look for
        sensitive_patterns = {
            "hardcoded_password": r'(?i)(password|pwd|pass)\s*=\s*["\'].*["\']',
            "api_key": r'(?i)(api_key|apikey|api_token)\s*=\s*["\'].*["\']',
            "secret_key": r'(?i)(secret_key|secret)\s*=\s*["\'].*["\']',
            "aws_key": r'(?i)(aws_access_key|aws_secret)\s*=\s*["\'].*["\']',
            "connection_string": r'(?i)(mongodb://|postgresql://|mysql://|redis://)',
        }
        
        for file_path, file_info in self.audit_data["files"].items():
            if not file_path.endswith(('.py', '.json', '.yml', '.yaml', '.env')):
                continue
                
            try:
                full_path = self.root / file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for issue_type, pattern in sensitive_patterns.items():
                    if matches := re.findall(pattern, content):
                        self.audit_data["security_issues"].append({
                            "file": file_path,
                            "type": issue_type,
                            "count": len(matches),
                            "severity": "high" if issue_type in ["api_key", "secret_key", "aws_key"] else "medium"
                        })
                        
            except Exception:
                pass
                
    def _find_duplicates(self):
        """Find duplicate files based on hash"""
        print("🔍 Finding duplicate files...")
        
        hash_to_files = {}
        
        for file_path, file_info in self.audit_data["files"].items():
            file_hash = file_info.get("hash")
            if file_hash:
                if file_hash in hash_to_files:
                    hash_to_files[file_hash].append(file_path)
                else:
                    hash_to_files[file_hash] = [file_path]
                    
        # Record duplicates
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.audit_data["duplicates"].append({
                    "hash": file_hash,
                    "files": files,
                    "count": len(files)
                })
                
    def _analyze_structure(self):
        """Analyze project structure"""
        print("📊 Analyzing project structure...")
        
        # Count files by directory
        dir_stats = {}
        
        for file_path in self.audit_data["files"]:
            dir_path = os.path.dirname(file_path) or "root"
            if dir_path not in dir_stats:
                dir_stats[dir_path] = {"count": 0, "size": 0, "types": {}}
                
            dir_stats[dir_path]["count"] += 1
            dir_stats[dir_path]["size"] += self.audit_data["files"][file_path]["size"]
            
            ext = self.audit_data["files"][file_path]["extension"]
            if ext not in dir_stats[dir_path]["types"]:
                dir_stats[dir_path]["types"][ext] = 0
            dir_stats[dir_path]["types"][ext] += 1
            
        self.audit_data["structure_analysis"]["directories"] = dir_stats
        
        # Identify key directories
        key_dirs = ["src", "tests", "scripts", "data", "docs", "database", "scrapers"]
        self.audit_data["structure_analysis"]["key_directories_present"] = [
            d for d in key_dirs if any(f.startswith(d + "/") for f in self.audit_data["files"])
        ]
        
    def _generate_statistics(self):
        """Generate overall statistics"""
        print("📈 Generating statistics...")
        
        stats = {
            "total_files": len(self.audit_data["files"]),
            "total_size": sum(f["size"] for f in self.audit_data["files"].values()),
            "file_types": {},
            "python_files": 0,
            "test_files": 0,
            "documentation_files": 0,
            "config_files": 0,
            "data_files": 0
        }
        
        # Count by type
        for file_path, file_info in self.audit_data["files"].items():
            ext = file_info["extension"]
            if ext not in stats["file_types"]:
                stats["file_types"][ext] = 0
            stats["file_types"][ext] += 1
            
            # Categorize files
            if ext == ".py":
                stats["python_files"] += 1
                if "test" in file_path.lower():
                    stats["test_files"] += 1
            elif ext in [".md", ".rst", ".txt"]:
                stats["documentation_files"] += 1
            elif ext in [".json", ".yml", ".yaml", ".toml", ".ini"]:
                stats["config_files"] += 1
            elif file_path.startswith("data/"):
                stats["data_files"] += 1
                
        self.audit_data["statistics"] = stats
        
    def _get_file_hash(self, path: Path) -> str:
        """Calculate file hash"""
        try:
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
            
    def _save_audit(self):
        """Save audit results"""
        output_path = self.root / "PROJECT_AUDIT.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_data, f, indent=2, ensure_ascii=False)
            
        # Also create a summary
        self._create_summary()
        
    def _create_summary(self):
        """Create human-readable summary"""
        summary_path = self.root / "AUDIT_SUMMARY.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 Manalytics Project Audit Summary\n\n")
            f.write(f"**Date**: {self.audit_data['metadata']['audit_date']}\n\n")
            
            # Statistics
            stats = self.audit_data['statistics']
            f.write("## 📈 Statistics\n\n")
            f.write(f"- Total files: {stats['total_files']}\n")
            f.write(f"- Total size: {stats['total_size']:,} bytes\n")
            f.write(f"- Python files: {stats['python_files']}\n")
            f.write(f"- Test files: {stats['test_files']}\n")
            f.write(f"- Documentation: {stats['documentation_files']}\n\n")
            
            # Security issues
            if self.audit_data['security_issues']:
                f.write("## 🔒 Security Issues Found\n\n")
                for issue in self.audit_data['security_issues']:
                    f.write(f"- **{issue['type']}** in `{issue['file']}` ({issue['severity']} severity)\n")
            else:
                f.write("## ✅ No Security Issues Found\n\n")
                
            # Duplicates
            if self.audit_data['duplicates']:
                f.write(f"\n## 🔄 Duplicate Files Found: {len(self.audit_data['duplicates'])}\n\n")
                for dup in self.audit_data['duplicates'][:5]:  # Show first 5
                    f.write(f"- {dup['count']} copies: {', '.join(dup['files'][:3])}\n")
                    
            # Structure
            f.write("\n## 📁 Project Structure\n\n")
            f.write("Key directories present: " + ", ".join(self.audit_data['structure_analysis']['key_directories_present']) + "\n")


if __name__ == "__main__":
    auditor = ProjectAuditor()
    auditor.run_full_audit()