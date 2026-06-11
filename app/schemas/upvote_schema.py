from pydantic import BaseModel
from typing import Literal

class VoteCreate(BaseModel):
    vote: Literal[1, -1]

    model_config = {
        "from_attributes" : True
    }