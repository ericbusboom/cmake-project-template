from invoke import task
import os
from pathlib import Path
import re

def get_current_project_name(proj_dir: Path):
    cmake_lists_path = proj_dir / "CMakeLists.txt"
    with cmake_lists_path.open(encoding='utf-8') as file:
        for line in file:
            match = re.match(r'project\((\w+)', line)
            if match:
                return match.group(1)
    raise ValueError("Project name not found in CMakeLists.txt")

def replace_text_in_file(file_path, old_text, new_text):
    file_contents = file_path.read_text(encoding='utf-8')
    file_contents = file_contents.replace(old_text, new_text)
    file_path.write_text(file_contents, encoding='utf-8')

def replace_in_all_files(directory, old_text, new_text):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "CMakeLists.txt" or root.endswith('/cmake'):
                file_path = Path(root) / file
                replace_text_in_file(file_path, old_text, new_text)


@task
def rename(c, new_project_name):
    """Rename the project, changing all occurances of the project name in CMake files"""

    proj_dir = Path.cwd()  # Set directory to the current directory
    current_project_name = get_current_project_name(proj_dir)
    uppercase_new_project_name = new_project_name.upper()

    old_texts = [current_project_name, current_project_name.upper()]
    new_texts = [new_project_name, uppercase_new_project_name]

    for old_text, new_text in zip(old_texts, new_texts):
        replace_in_all_files(directory, old_text, new_text)

@task
def update_h(c):
    """Add any .h or .hpp files in the include directory to the CMake file"""
    proj_dir = Path.cwd()
    project_name = get_current_project_name(proj_dir)
    include_dir = proj_dir / 'include'
    header_files = [f.name for f in include_dir.glob('*.h')] + [f.name for f in include_dir.glob('*.hpp')]

    set_command = f"set({project_name}_INC\n    " +\
                    '\n    '.join(header_files) +\
                    "\n    )\n"

    cmake_lists_path = include_dir / 'CMakeLists.txt'
    cmake_lists_contents = cmake_lists_path.read_text(encoding='utf-8')

    # Build regex dynamically based on project name
    regex = re.compile(rf'set\({re.escape(project_name)}_INC.*?\)', re.DOTALL)
    new_contents = re.sub(regex, set_command, cmake_lists_contents)

    cmake_lists_path.write_text(new_contents, encoding='utf-8')

@task
def update_src(c):
    proj_dir = Path.cwd()
    project_name = get_current_project_name(proj_dir)
    src_dir = proj_dir / 'src'
    source_files = [f.name for f in src_dir.glob('*.c')] + [f.name for f in src_dir.glob('*.cpp')]

    set_command = f"set({project_name}_SRC\n    " + '\n    '.join(source_files) + "\n    )\n"

    cmake_lists_path = src_dir / 'CMakeLists.txt'
    cmake_lists_contents = cmake_lists_path.read_text(encoding='utf-8')

    # Build regex dynamically based on project name
    regex = re.compile(rf'set\({re.escape(project_name)}_SRC.*?\)', re.DOTALL)
    new_contents = re.sub(regex, set_command, cmake_lists_contents, count=1)

    cmake_lists_path.write_text(new_contents, encoding='utf-8')



@task
def rebuild(c):
    # Call update_h and update_src tasks
    update_h(c)
    update_src(c)

    # Rebuild the project with CMake and Make
    with c.cd(str(Path.cwd())):
        c.run("cmake .")
        c.run("make")

if __name__ == "__main__":
    import invoke
    invoke.run()
