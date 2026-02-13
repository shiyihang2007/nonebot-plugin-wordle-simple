from pydantic import BaseModel


class ScopedConfig(BaseModel):
    command_priority: int = 10

    groups_enabled: set[str] = set()
    ban_user: set[str] = set()

    length_min: int = 4
    length_max: int = 12

    debug_enabled: bool = False

    font_path: str = "./resources/FiraCode-Medium.ttf"
    dictionary_answer_path: str = "./resources/DictionaryAnswer.txt"
    dictionary_guess_path: str = "./resources/DictionaryGuess.txt"


class Config(BaseModel):
    wordle: ScopedConfig
