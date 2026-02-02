import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]
        if args:
            command.extend(args)

        completed_process = subprocess.run(command, capture_output=True, cwd=working_dir_abs, timeout=30, text=True)

        output_string = ""

        if completed_process.returncode != 0:
            output_string = f"Process exited with code {completed_process.returncode}."
        elif not completed_process.stdout or completed_process.stderr:
            output_string += " No output produced"
        else:
            output_string += f"\nSTDOUT: {completed_process.stdout}\nSTDERR: {completed_process.stderr}"

        return output_string
    
    except Exception as e:
        f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python file from a specified file path relative to the working directory, with the provided arguments, if any are given",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING
                ),
                description="Optional arguments which can be provided to the executed file"
            ),
        },
        required=["file_path"]
    ),
)