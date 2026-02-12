from click.testing import CliRunner
from ralf.main import cli
from importlib.metadata import version

def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    # Retrieve the version from the installed package to compare
    assert result.output.strip() == version("ralf")
