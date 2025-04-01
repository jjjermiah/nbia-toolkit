# from enum import StrEnum, auto
from pathlib import Path
from typing import Tuple, Type

from pydantic import BaseModel, Field
from pydantic_settings import (
	BaseSettings,
	PydanticBaseSettingsSource,
	SettingsConfigDict,
	TomlConfigSettingsSource,
)

from nbiatoolkit.config import dirs


class APISettings(BaseModel):
	"""Settings that control API request behavior such as retries, timeouts, and concurrency."""

	max_attempts: int = Field(
		default=10,
		description=(
			'Maximum number of retry attempts for a failed API request. '
			'Used with exponential backoff strategy. '
			'Set this lower to fail faster on persistent errors.'
		),
	)

	wait_multiplier: float = Field(
		default=1.0,
		description=(
			'Multiplier for exponential backoff wait time between retries. '
			'For example, if min_wait=1 and multiplier=2, retries will occur at 1s, 2s, 4s, etc.'
		),
	)

	min_wait: int = Field(
		default=1,
		description='Minimum wait time (in seconds) before retrying a failed request.',
	)

	max_wait: int = Field(
		default=25, description='Maximum wait time (in seconds) between retry attempts.'
	)

	max_concurrent_requests: int = Field(
		default=5,
		description=(
			'Maximum number of concurrent API requests allowed. '
			'This value sets the size of the asyncio semaphore used to throttle parallel requests. '
			'Increase this for faster bulk processing, or lower it to avoid rate-limiting.'
		),
	)

	timeout_seconds: float = Field(
		default=30.0,
		description=(
			'Maximum total time (in seconds) to wait for a single API request to complete. '
			'Includes connection, read, and response time. '
			"Used to set aiohttp's ClientTimeout."
		),
	)


class Login(BaseModel):
	"""Login Credentials"""

	nbia_username: str = Field('nbia_guest', description='NBIA Username')
	nbia_password: str = Field('', description='NBIA Password')

	def write_toml(self, toml_path: Path) -> None:
		import toml  # noqa

		data = self.model_dump()

		with toml_path.open('w') as toml_file:
			toml.dump(data, toml_file)


class Settings(BaseSettings):
	"""

	Order of precedence:

	1. '~/.config/nbiatoolkit/settings.toml'
	    [login]
	    nbia_username = "username"
	    nbia_password = "password"

	2. .env file
	    LOGIN__NBIA_USERNAME="username"
	    LOGIN__NBIA_PASSWORD="password"

	3. Environment Variables
	    export LOGIN__NBIA_USERNAME="username"
	    export LOGIN__NBIA_PASSWORD="password"

	# TODO: implement docker secrets /run/secrets/nbia_username /run/secrets/nbia_password
	"""

	# project_name: str | None = None
	login: Login = Login()
	api: APISettings = APISettings()

	model_config = SettingsConfigDict(
		# to instantiate the Login class, the variable name would be login.nbia_username in the environment
		env_nested_delimiter='__',
		env_file='.env',
		env_file_encoding='utf-8',
		# Global settings file
		toml_file=dirs.user_config_path / 'settings.toml',
		# allow for other fields to be present in the config file
		# this allows for the config file to be used for other purposes
		# but also for users to define anything else they might want
		extra='ignore',
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

	@property
	def NBIA_USERNAME(self) -> str:
		return self.login.nbia_username

	@property
	def NBIA_PASSWORD(self) -> str:
		return self.login.nbia_password

	@property
	def json_schema(self) -> dict:
		"""Return the JSON schema for the settings."""
		return self.model_json_schema()


if __name__ == '__main__':
	from rich import print
	import json

	settings = Settings()

	schema = Settings().json_schema
	schema_path = Path('schemas/settings.schema.json')
	schema_path.parent.mkdir(parents=True, exist_ok=True)
	schema_path.write_text(json.dumps(schema, indent=2))

	print(f'Saved schema to {schema_path}')
	# add "#:schema settings.schema.json" to the top of the toml file