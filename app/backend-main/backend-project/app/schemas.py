from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScanRequest(BaseModel):
    url: str
    domain: str
    screenshot_hash: str | None = None


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    domain: str
    screenshot_hash: str | None = None
    status: str
    created_at: datetime


class ScanListResponse(BaseModel):
    scans: list[ScanResponse]


class ScanUpdateRequest(BaseModel):
    url: str | None = None
    domain: str | None = None
    screenshot_hash: str | None = None
    status: str | None = None


class ResultCreate(BaseModel):
    scan_id: int
    risk_score: float = Field(ge=0.0, le=1.0)
    classification: str
    details_json: dict[str, Any] | None = None
    model_version: str | None = None


class ResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_id: int
    risk_score: float
    classification: str
    details_json: dict[str, Any] | None = None
    model_version: str | None = None
    created_at: datetime


class ResultListResponse(BaseModel):
    results: list[ResultResponse]


class FeedbackCreate(BaseModel):
    result_id: int
    user_verdict: str
    comment: str | None = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    result_id: int
    user_verdict: str
    comment: str | None = None
    created_at: datetime


class FeedbackListResponse(BaseModel):
    feedbacks: list[FeedbackResponse]


class WhitelistCreate(BaseModel):
    domain: str
    logo_hash: str | None = None


class WhitelistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    logo_hash: str | None = None
    verified_at: datetime


class WhitelistCheckResponse(BaseModel):
    domain: str
    whitelisted: bool
    matched_logo_hash: str | None = None


class HashCheckRequest(BaseModel):
    screenshot_hash: str
    max_distance: int = Field(default=8, ge=0, le=64)


class HashMatch(BaseModel):
    scan_id: int
    distance: int


class HashCheckResponse(BaseModel):
    exact_match: bool
    nearest_match: HashMatch | None = None


class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRoleUpdate(BaseModel):
    role: str


class BrandCreate(BaseModel):
    name: str
    domains: list[str] = Field(default_factory=list)
    logo_embeddings: list[float] | None = None
    colors_json: dict[str, Any] | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    domains: list[str] | None = None
    logo_embeddings: list[float] | None = None
    colors_json: dict[str, Any] | None = None


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domains: list[str]
    logo_embeddings: list[float] | None = None
    colors_json: dict[str, Any] | None = None


class BrandListResponse(BaseModel):
    brands: list[BrandResponse]
