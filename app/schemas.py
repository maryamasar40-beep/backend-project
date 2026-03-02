from pydantic import BaseModel
from typing import Optional



class ScanRequest(BaseModel):
    url: str
    domain: str
    screenshot_hash: Optional[str] = None


class ScanResponse(BaseModel):
    id: int
    url: str
    domain: str
    screenshot_hash: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ScanListResponse(BaseModel):
    all_scans: list[ScanResponse]
    
class ScanUpdateRequest(BaseModel):
    url: str
    domain: str
    screenshot_hash: Optional[str] = None
    status: str