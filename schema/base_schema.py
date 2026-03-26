from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class BaseSQLSchema(SQLModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
