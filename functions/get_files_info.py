import os


def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
    valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs

    if not valid_target_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory' 
    
    file_info = []

    try:
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                file_info.append(f"- {item}: file_size={os.path.getsize(item_path)}, is_dir={True}")
            else:
                file_info.append(f"- {item}: file_size={os.path.getsize(item_path)}, is_dir={False}")
    except Exception as e:
        return f"Error: {e}"
    
    return "\n   ".join(file_info)