# from enum import StrEnum, auto
from pathlib import Path
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class Login(BaseModel):
    """Login Credentials

    Order of precedence:

    1. Environment Variables
        - LOGIN__NBIA_USERNAME
        - LOGIN__NBIA_PASSWORD

    2. .env file
        - LOGIN__NBIA_USERNAME
        - LOGIN__NBIA_PASSWORD

    3. '~/.config/nbiatoolkit/settings.toml'
        - [login]
            - nbia_username
            - nbia_password

    # TODO: implement docker secrets /run/secrets/nbia_username /run/secrets/nbia_password
    """

    nbia_username: str = "nbia_guest"
    nbia_password: str = ""

    def write_toml(self, path: Path) -> None:
        import toml  # noqa

        data = {
            "login": {
                "nbia_username": self.nbia_username,
                "nbia_password": self.nbia_password,
            }
        }
        with path.open("w") as toml_file:
            toml.dump(data, toml_file)


class Settings(BaseSettings):
    # project_name: str | None = None
    login: Login = Login()

    model_config = SettingsConfigDict(
        # to instantiate the Login class, the variable name would be login.nbia_username in the environment
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        # unsure if i want to use yamls
        # yaml_file="nbia.yaml",
        # Global settings file
        toml_file=Path("~/.config", "nbiatoolkit").resolve() / "settings.toml",
        # allow for other fields to be present in the config file
        # this allows for the config file to be used for other purposes
        # but also for users to define anything else they might want
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            # file_secret_settings,
            init_settings,
            TomlConfigSettingsSource(settings_cls),
        )
