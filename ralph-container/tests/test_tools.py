import os
import tempfile
import shutil
import pytest
from ralph.agent import list_files, read_file, write_file, run_command, done

def test_file_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"configurable": {"workdir": tmpdir}}

        # Test write_file
        # We can pass relative path now
        result = write_file.invoke({"path": "test.txt", "content": "Hello World"}, config=config)
        assert "Successfully wrote" in result
        file_path = os.path.join(tmpdir, "test.txt")
        assert os.path.exists(file_path)

        # Test read_file
        content = read_file.invoke({"path": "test.txt"}, config=config)
        assert content == "Hello World"

        # Test list_files
        files = list_files.invoke({"path": "."}, config=config)
        assert "test.txt" in files

        # Test read_file non-existent
        result = read_file.invoke({"path": "nonexistent.txt"}, config=config)
        assert "Error reading file" in result

def test_security_checks():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve symlinks in tmpdir for consistent comparison
        tmpdir = os.path.realpath(tmpdir)
        config = {"configurable": {"workdir": tmpdir}}

        # Create a file outside workdir
        outside_dir = tempfile.mkdtemp()
        outside_dir = os.path.realpath(outside_dir)
        try:
            outside_file = os.path.join(outside_dir, "secret.txt")
            with open(outside_file, "w") as f:
                f.write("secret")

            # Try to read outside file using absolute path
            # The tool catches exceptions and returns error string
            result = read_file.invoke({"path": outside_file}, config=config)
            assert "Path traversal attempt detected" in result

            # Try to write outside
            result = write_file.invoke({"path": os.path.join(outside_dir, "evil.txt"), "content": "evil"}, config=config)
            assert "Path traversal attempt detected" in result

            # Try relative path traversal
            # Depending on OS, verify strict relative check
            # We can't easily guess relative path to outside_dir, but we can try "../"
            result = list_files.invoke({"path": ".."}, config=config)
            assert "Path traversal attempt detected" in str(result) or "Error" in str(result)

        finally:
            shutil.rmtree(outside_dir)

def test_missing_context():
    # invoked without config
    # The tool should catch the ValueError and return it as string
    result = list_files.invoke({"path": "."})
    assert "Workdir not found" in str(result)

    result = read_file.invoke({"path": "test.txt"})
    assert "Workdir not found" in str(result)

def test_run_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = os.path.realpath(tmpdir)
        config = {"configurable": {"workdir": tmpdir}}

        # Verify pwd matches workdir
        result = run_command.invoke({"command": "pwd"}, config=config)
        assert tmpdir in result

        # Test a command that writes to stderr
        result = run_command.invoke({"command": "ls /nonexistent_directory_xyz"}, config=config)
        assert "stderr" in result

def test_done():
     with tempfile.TemporaryDirectory() as tmpdir:
        config = {"configurable": {"workdir": tmpdir}}
        result = done.invoke({}, config=config)
        assert result == "RALPH_DONE"
