from invoke import task
import os
from pathlib import Path

@task
def rename(c, project_name):
    def replace_text_in_file(file_path, old_text, new_text):
        file_contents = file_path.read_text()
        file_contents = file_contents.replace(old_text, new_text)
        file_path.write_text(file_contents )

    def replace_in_all_files(directory, old_text, new_text):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                replace_text_in_file(file_path, old_text, new_text)

    directory = Path.cwd()  # Set directory to the current directory
    uppercase_project_name = project_name.upper()

    old_texts = ['-h', 'CMAKEDEMO']
    new_texts = [project_name, uppercase_project_name]

    for old_text, new_text in zip(old_texts, new_texts):
        replace_in_all_files(directory, old_text, new_text)
