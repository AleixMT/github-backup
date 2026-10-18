import os


def is_file_directory_writable(file_path: str) -> bool:
    return os.access(os.path.dirname(os.path.abspath(file_path)), os.W_OK)


def is_file_writable(file_path: str) -> bool:
    # Check permissions without opening the file, so an existing file is not truncated
    if os.path.exists(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.W_OK)
    return is_file_directory_writable(file_path)


def read_file(file_path: str) -> str:
    """
    Reads the GH_TOKEN file and returns its content.
    Handles edge cases such as the file being empty, not existing, or being unreadable.

    Args:
        file_path (str): Path to the token file.

    Returns:
        str: The content of the token file if valid.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read due to permission issues.
        ValueError: If the file is empty or contains only whitespace.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        # Check if the file is readable
        if not os.access(file_path, os.R_OK):
            raise PermissionError(
                f"The file '{file_path}' cannot be read. Check permissions."
            )

        # Read the file
        with open(file_path) as file:
            content = file.read().strip()

        # Check if the file is empty or contains only whitespace
        if not content:
            raise ValueError(
                f"The file '{file_path}' is empty or contains only whitespace."
            )

        return content

    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except ValueError:
        raise
    except Exception:
        raise


def read_env_var(var_name: str) -> str:
    """
    Reads an environment variable and validates its content.

    Args:
        var_name (str): Name of the environment variable.

    Returns:
        str: The value of the environment variable if valid.

    Raises:
        KeyError: If the environment variable does not exist.
        ValueError: If the environment variable is empty or contains only whitespace.
    """
    try:
        # Check if the environment variable exists
        if var_name not in os.environ:
            raise KeyError(f"The environment variable '{var_name}' does not exist.")

        # Read the value
        value = os.environ[var_name].strip()

        # Check if the value is empty or contains only whitespace
        if not value:
            raise ValueError(
                f"The environment variable '{var_name}' is empty or contains only whitespace."
            )

        return value

    except KeyError as e:
        print(f"Error: {e}")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
