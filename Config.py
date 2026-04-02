from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class Config(BaseSettings):
    width: int = Field(default=20)
    height: int = Field(default=20)
    entry: str | tuple[int, int] = Field(default=(0, 0))
    exit: str | tuple[int, int] = Field(default=(20, 20))
    output_file: str = Field(default="maze.txt")
    perfect: bool = Field(default=False)
    seed: str = Field(default='42')

    model_config = SettingsConfigDict(
        env_file="config.txt"
    )

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def decode_tuple(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(',')]
        return v

    @model_validator(mode='after')
    def decode_dict(self) -> Self:
        if self.entry[0] < 0:
            raise Exception(
                f"Invalid entry Coordinate x: {self.entry[0]} is negative")
        if self.entry[1] < 0:
            raise Exception(
                f"Invalid entry Coordinate y: {self.entry[0]} is negative")
        if self.exit[0] < 0:
            raise Exception(
                f"Invalid entry Coordinate x: {self.entry[0]} is negative")
        if self.exit[1] < 0:
            raise Exception(
                f"Invalid entry Coordinate y: {self.entry[0]} is negative")
        if self.entry[0] > self.width:
            raise Exception(
                f"Invalid entry Coordinate x: {self.entry[0]} is out of maze width: {self.width}")
        if self.entry[1] > self.height:
            raise Exception(
                f"Invalid entry Coordinate x: {self.entry[1]} is out of maze width: {self.height}")
        if self.exit[0] > self.width:
            raise Exception(
                f"Invalid entry Coordinate x: {self.exit[0]} is out of maze width: {self.width}")
        if self.exit[1] > self.height:
            raise Exception(
                f"Invalid entry Coordinate x: {self.exit[1]} is out of maze width: {self.height}")
        return self
