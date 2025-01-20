import re
from pathlib import Path

def get_project_root():
    """
    Returns the project root directory based on the known structure.
    """
    return Path("/Users/oceanheart/Documents/code/meet-ben")

def extract_import_files(markdown_path):
    """
    Extracts the list of markdown file paths from markdown-style links 
    within <import-files></import-files> tags.
    """
    with open(markdown_path, 'r') as md_file:
        content = md_file.read()

    match = re.search(r'<import-files>(.*?)</import-files>', content, re.DOTALL)
    if match:
        # Extract markdown-style links and get their pathnames
        file_links = re.findall(r'\[.*?\]\((.*?)\)', match.group(1))
        return [f"app/utils/{file.strip()}" for file in file_links]
    else:
        return []

def import_markdown_content(file_paths, output_path, project_root):
    """
    Reads content from each markdown file in file_paths and appends it to output_path.
    Resolves paths relative to the project root.
    """
    output_file = Path(output_path)
    output_file.write_text("")  # Clear the output file if it exists

    content = ""

    for file_path in file_paths:
        absolute_path = project_root / file_path
        if absolute_path.is_file():
            with open(absolute_path, 'r') as f:
                content = content + f.read()
                
        else:
            print(f"Warning: File not found - {absolute_path}")

    return content

if __name__ == "__main__":
    project_root = get_project_root()  # Set the project root dynamically
    markdown_file = project_root / "specs/spec_update_agent.md"  # Path to the main markdown file
    output_file = project_root / "specs/spec_update_agent_imported.md"  # Path for the output file

    files_to_import = extract_import_files(markdown_file)
    print(files_to_import)
    content = import_markdown_content(files_to_import, output_file, project_root)
    
    with open(markdown_file, 'r') as md_file:
        text = md_file.read()
        replaced_text = text.replace("{{imported_content}}", content)

        with open(output_file, 'w') as out:
            out.write(replaced_text)
