from pydantic import BaseModel
from typing import Literal


class GitHubTreeItem(BaseModel):
    path: str
    mode: str
    type: Literal["blob", "tree"]
    sha: str