from pydantic import BaseModel, Field


class ReadmeContent(BaseModel):
    """
    Structured information extracted from a README.
    """

    title: str = ""
    tagline: str = ""
    description: str = ""

    headings: list[str] = Field(default_factory=list)

    badges: list[str] = Field(default_factory=list)

    links: list[str] = Field(default_factory=list)

    images: list[str] = Field(default_factory=list)

    code_blocks: int = 0

    sections: dict[str, str] = Field(default_factory=dict)