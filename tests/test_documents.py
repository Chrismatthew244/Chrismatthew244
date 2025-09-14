import os
import shutil
import tempfile

from fastapi.testclient import TestClient


def setup_app():
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["STORAGE_DIR"] = tmpdir
    os.environ["API_KEY"] = "testkey"
    from app.main import app
    return app, tmpdir


def test_upload_and_manage_document():
    app, tmpdir = setup_app()
    client = TestClient(app)
    file_content = b"hello world"
    response = client.post(
        "/documents/",
        headers={"X-API-Key": "testkey"},
        files={"file": ("test.txt", file_content)},
        data={"customer": "cust", "task": "task"},
    )
    assert response.status_code == 200, response.text
    doc_id = response.json()["id"]

    response = client.get(f"/documents/{doc_id}", headers={"X-API-Key": "testkey"})
    assert response.status_code == 200

    preview = client.get(f"/documents/{doc_id}/preview", headers={"X-API-Key": "testkey"})
    assert preview.status_code == 200
    assert "preview" in preview.json()

    delete = client.delete(f"/documents/{doc_id}", headers={"X-API-Key": "testkey"})
    assert delete.status_code == 200

    shutil.rmtree(tmpdir)
