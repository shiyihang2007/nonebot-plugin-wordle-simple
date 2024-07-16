from pydantic import BaseModel


class ScopedConfig(BaseModel):
    command_priority: int = 10

    groups_enabled: set[str] = {}
    ban_user: set[str] = {}

    length_min: int = 4
    length_max: int = 12

    debug_enabled: bool = False


class Config(BaseModel):
    wordle: ScopedConfig
