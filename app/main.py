from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, schemas, storage
from .database import Base, engine, get_db
from .dependencies import require_api_key

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/files", StaticFiles(directory=storage.STORAGE_DIR), name="files")


@app.post("/documents/", response_model=schemas.DocumentOut, dependencies=[Depends(require_api_key)])
async def upload_document(
    customer: str = Form(...),
    task: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    path = storage.save_file(file)
    doc = models.Document(filename=file.filename, path=path, customer=customer, task=task)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return schemas.DocumentOut(
        id=doc.id,
        filename=doc.filename,
        url=storage.get_file_url(doc.path),
        customer=doc.customer,
        task=doc.task,
    )


@app.get("/documents/{doc_id}", response_model=schemas.DocumentOut, dependencies=[Depends(require_api_key)])
def read_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return schemas.DocumentOut(
        id=doc.id,
        filename=doc.filename,
        url=storage.get_file_url(doc.path),
        customer=doc.customer,
        task=doc.task,
    )


@app.delete("/documents/{doc_id}", dependencies=[Depends(require_api_key)])
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    storage.delete_file(doc.path)
    db.delete(doc)
    db.commit()
    return {"ok": True}


@app.get("/documents/{doc_id}/preview", dependencies=[Depends(require_api_key)])
def preview_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    path = doc.path
    if path.endswith((".txt", ".md")):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return {"preview": f.read(200)}
    return {"detail": "Preview not available"}
