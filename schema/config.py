from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

common_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
)
