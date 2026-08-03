from pydantic import BaseModel, Field


class RepositoryIdentity(BaseModel):
    """
    Canonical understanding of what this repository actually is.
    """

    product_name: str = ""

    category: str = ""

    subtype: str = ""

    tagline: str = ""

    description: str = ""

    audience: str = ""

    capabilities: list[str] = Field(default_factory=list)

    confidence: float = 0.0

    evidence: list[str] = Field(default_factory=list)


class RepositoryIdentityEvidence(BaseModel):
    """
    Structured evidence used to infer repository identity.
    """

    title: str = ""

    tagline: str = ""

    description: str = ""

    topics: list[str] = Field(default_factory=list)

    frontend: list[str] = Field(default_factory=list)

    backend: list[str] = Field(default_factory=list)

    languages: list[str] = Field(default_factory=list)

    directories: list[str] = Field(default_factory=list)

    readme_sections: list[str] = Field(default_factory=list)