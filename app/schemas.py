from pydantic import BaseModel


class DocumentBase(BaseModel):
    customer: str
    task: str


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: int
    filename: str
    url: str

    class Config:
        orm_mode = True
