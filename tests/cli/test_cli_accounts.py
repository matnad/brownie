#!/usr/bin/python3

import json

import pytest

from brownie._cli import accounts as cli_accounts
from brownie._config import _get_data_folder


@pytest.fixture(autouse=True)
def no_pass(monkeypatch):
    monkeypatch.setattr("brownie.network.account.getpass", lambda x: "")


def test_new_account(monkeypatch, runner):
    assert not _get_data_folder().joinpath("accounts/new.json").exists()
    result = runner.invoke(cli_accounts._list)
    assert "0x3b9b63C67838C9fef6c50e3a06f574Be12b3D50f" not in result.output
    monkeypatch.setattr(
        "builtins.input",
        lambda x: "0x60285766d7296d0744450696603d9593513958fdbb494cc6d234a5a797a2108f",
    )

    result = runner.invoke(cli_accounts.new, ["new"])
    assert result.exception is None
    assert "SUCCESS" in result.output

    result = runner.invoke(cli_accounts._list)
    assert "0x3b9b63C67838C9fef6c50e3a06f574Be12b3D50f" in result.output
    assert _get_data_folder().joinpath("accounts/new.json").exists()


def test_generate(runner):
    path = _get_data_folder().joinpath("accounts/generate.json")
    assert not path.exists()

    result = runner.invoke(cli_accounts.generate, ["generate"])
    assert result.exception is None
    assert "SUCCESS" in result.output

    assert path.exists()
    with path.open() as fp:
        data = json.load(fp)
    result = runner.invoke(cli_accounts._list)
    assert data["address"] in result.output.lower()


def test_import(runner):
    path = _get_data_folder().joinpath("accounts/import-test.json")

    result = runner.invoke(cli_accounts.generate, ["import-test"])
    assert result.exception is None
    assert "SUCCESS" in result.output

    new_path = _get_data_folder().joinpath("x.json")
    path.rename(new_path)
    runner.invoke(cli_accounts._import, ["import-new", str(new_path.absolute())])
    assert _get_data_folder().joinpath("accounts/import-new.json").exists()


def test_import_already_exists(runner):
    runner.invoke(cli_accounts.generate, ["import-exists"])
    path = _get_data_folder().joinpath("accounts/import-exists.json")

    result = runner.invoke(cli_accounts._import, ["import-exists", str(path)])
    assert isinstance(result.exception, FileExistsError) is True
    assert "SUCCESS" not in result.output


def test_export(runner):
    runner.invoke(cli_accounts.generate, ["export-test"])
    target_path = _get_data_folder().joinpath("exported.json")
    assert not target_path.exists()

    result = runner.invoke(cli_accounts.export, ["export-test", str(target_path.absolute())])
    assert result.exception is None
    assert "SUCCESS" in result.output

    assert target_path.exists()


def test_export_not_exists(runner):
    path = _get_data_folder().joinpath("accounts/nothing.json")

    result = runner.invoke(cli_accounts.export, ["unknown", str(path)])
    assert isinstance(result.exception, FileNotFoundError) is True
    assert "SUCCESS" not in result.output


def test_export_overwrite(runner):
    runner.invoke(cli_accounts.generate, ["export-exists"])
    path = str(_get_data_folder().joinpath("accounts/export-exists.json").absolute())

    result = runner.invoke(cli_accounts.export, ["export-exists", path])
    assert isinstance(result.exception, FileExistsError) is True
    assert "SUCCESS" not in result.output


def test_password(monkeypatch, accounts, runner):
    runner.invoke(cli_accounts.generate, ["pw-test"])
    passwords = ["xxx", "xxx", ""]
    monkeypatch.setattr("brownie.network.account.getpass", lambda x: passwords.pop())

    result = runner.invoke(cli_accounts.password, ["pw-test"])
    assert result.exception is None
    assert "SUCCESS" in result.output

    accounts.load("pw-test")


def test_delete(runner):
    runner.invoke(cli_accounts.generate, ["del-test"])
    path = _get_data_folder().joinpath("accounts/del-test.json")
    assert path.exists()

    result = runner.invoke(cli_accounts.delete, ["del-test"])
    assert result.exception is None
    assert "SUCCESS" in result.output

    assert not path.exists()
