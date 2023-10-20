from invoke import task
import os
from pathlib import Path
import re

@task
def rename(c, new_project_name):
    def get_current_project_name():
        cmake_lists_path = directory / "CMakeLists.txt"
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

    directory = Path.cwd()  # Set directory to the current directory
    current_project_name = get_current_project_name()
    uppercase_new_project_name = new_project_name.upper()

    old_texts = [current_project_name, current_project_name.upper()]
    new_texts = [new_project_name, uppercase_new_project_name]

    for old_text, new_text in zip(old_texts, new_texts):
        replace_in_all_files(directory, old_text, new_text)

if __name__ == "__main__":
    import invoke
    invoke.run()
