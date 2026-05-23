import pytest  # type: ignore[import-not-found]

from assistant.config import load_config


def test_load_config_from_yaml(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    yaml_file = tmp_path / 'config.yaml'
    yaml_file.write_text('api_key: yaml_key\napi_host: http://yaml_host/v1/\ntemperature: 0.5\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.delenv('API_HOST', raising=False)

    config = load_config()

    assert config.api_key == 'yaml_key'
    assert config.temperature == 0.5


def test_load_config_env_overrides_yaml(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    yaml_file = tmp_path / 'config.yaml'
    yaml_file.write_text('api_key: yaml_key\napi_host: http://yaml_host/v1/\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_KEY', 'env_key')

    config = load_config()

    assert config.api_key == 'env_key'
    assert config.api_host == 'http://yaml_host/v1/'


def test_load_config_exits_when_no_api_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.setenv('API_HOST', 'http://localhost/')

    with pytest.raises(SystemExit):
        load_config()
