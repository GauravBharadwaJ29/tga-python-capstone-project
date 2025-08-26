import os

INCLUDE_EXTENSIONS = (
    '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.md',
    '.Dockerfile', 'docker-compose.yml', 'requirements.txt', 'Makefile'
)
EXCLUDE_DIRS = {'node_modules', 'venv', '__pycache__', '.git', '.idea', '.vscode', 'dist', 'build'}

def should_include(filename):
    return filename.endswith(INCLUDE_EXTENSIONS) or os.path.basename(filename) in INCLUDE_EXTENSIONS

def main():
    project_root = input("Enter your project folder path: ").strip()
    output_file = input("Enter output Markdown file name (with .md extension): ").strip()

    with open(output_file, 'w', encoding='utf-8') as out:
        for dirpath, dirnames, filenames in os.walk(project_root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for filename in filenames:
                if should_include(filename):
                    filepath = os.path.join(dirpath, filename)
                    relpath = os.path.relpath(filepath, project_root)
                    out.write(f"\n\n## File: `{relpath}`\n\n")
                    ext = os.path.splitext(filename)[1]
                    lang = {
                        '.py': 'python',
                        '.js': 'javascript',
                        '.ts': 'typescript',
                        '.json': 'json',
                        '.yaml': 'yaml',
                        '.yml': 'yaml',
                        '.env': '',
                        '.md': 'markdown',
                        '.Dockerfile': 'dockerfile',
                        'docker-compose.yml': 'yaml',
                        'requirements.txt': '',
                        'Makefile': 'make'
                    }.get(ext, '')
                    out.write(f"\n\n## File: `{relpath}`\n\n")
                    out.write(f"```{lang}\n") 
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"# Error reading file: {e}")
                    out.write("\n```\n")

    print(f"\nDone! Your codebase is saved as '{output_file}' in Markdown format.")

if __name__ == "__main__":
    main()
# This script dumps the codebase into a Markdown file, including all relevant files and directories..not