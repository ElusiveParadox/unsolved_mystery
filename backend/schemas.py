from pydantic import BaseModel, StringConstraints
from typing import Annotated, List


class QueryRequest(BaseModel):
    question: str
    strict: bool = True


class EvidenceChunk(BaseModel):
    content: str
    source: str


class QueryResponse(BaseModel):
    answer: str
    citations: List[str]
    chunks: List[EvidenceChunk]


class UserAuth(BaseModel):
    username: str
    password: Annotated[
        str,
        StringConstraints(min_length=4, max_length=72)
    ]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
