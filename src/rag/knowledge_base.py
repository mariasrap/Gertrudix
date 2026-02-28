import os
import subprocess
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"


def list_files() -> dict:
    """List all knowledge files organized by folder."""
    if not DATA_DIR.exists():
        return {}

    structure = {}
    for item in sorted(DATA_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            files = []
            for f in sorted(item.rglob('*')):
                if f.is_file() and not f.name.startswith('.'):
                    files.append({
                        "name": f.name,
                        "path": str(f.relative_to(DATA_DIR)),
                        "size": f.stat().st_size
                    })
            if files:
                structure[item.name] = files
        elif item.is_file() and not item.name.startswith('.'):
            if "root" not in structure:
                structure["root"] = []
            structure["root"].append({
                "name": item.name,
                "path": item.name,
                "size": item.stat().st_size
            })

    return structure


def search(query: str, case_insensitive: bool = True) -> list[dict]:
    """Search for query in all text files using grep."""
    if not DATA_DIR.exists():
        return []

    flags = ["-r", "-l", "-n", "--include=*.txt", "--include=*.md"]
    if case_insensitive:
        flags.append("-i")

    try:
        result = subprocess.run(
            ["grep"] + flags + [query, str(DATA_DIR)],
            capture_output=True,
            text=True
        )

        matches = []
        for line in result.stdout.strip().split('\n'):
            if line:
                filepath = Path(line)
                if filepath.exists():
                    matches.append({
                        "path": str(filepath.relative_to(DATA_DIR)),
                        "name": filepath.name
                    })

        return matches
    except Exception as e:
        return [{"error": str(e)}]


def search_with_context(query: str, context_lines: int = 2) -> list[dict]:
    """Search and return matching lines with context."""
    if not DATA_DIR.exists():
        return []

    flags = ["-r", "-n", "-i", f"-C{context_lines}", "--include=*.txt", "--include=*.md"]

    try:
        result = subprocess.run(
            ["grep"] + flags + [query, str(DATA_DIR)],
            capture_output=True,
            text=True
        )

        matches = []
        current_file = None
        current_content = []

        for line in result.stdout.split('\n'):
            if not line:
                continue
            if line.startswith('--'):
                if current_file and current_content:
                    matches.append({
                        "file": current_file,
                        "content": '\n'.join(current_content)
                    })
                    current_content = []
                continue

            # Parse grep output: filename:linenum:content
            if ':' in line:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    filepath = Path(parts[0])
                    rel_path = str(filepath.relative_to(DATA_DIR)) if DATA_DIR in filepath.parents or filepath.parent == DATA_DIR else parts[0]
                    if current_file != rel_path:
                        if current_file and current_content:
                            matches.append({
                                "file": current_file,
                                "content": '\n'.join(current_content)
                            })
                        current_file = rel_path
                        current_content = []
                    current_content.append(parts[2])

        if current_file and current_content:
            matches.append({
                "file": current_file,
                "content": '\n'.join(current_content)
            })

        return matches
    except Exception as e:
        return [{"error": str(e)}]


def load_file(path: str) -> str:
    """Load content from a specific file."""
    filepath = DATA_DIR / path
    if not filepath.exists():
        return f"Error: File not found: {path}"
    if not filepath.is_file():
        return f"Error: Not a file: {path}"

    try:
        if filepath.suffix.lower() == '.pdf':
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                return '\n'.join(page.extract_text() for page in reader.pages)
            except ImportError:
                return "Error: pypdf not installed for PDF support"
        else:
            return filepath.read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading file: {e}"


def get_stats() -> dict:
    """Get statistics about the knowledge base."""
    structure = list_files()
    total_files = sum(len(files) for files in structure.values())
    return {
        "folders": list(structure.keys()),
        "total_files": total_files,
        "data_dir": str(DATA_DIR)
    }
