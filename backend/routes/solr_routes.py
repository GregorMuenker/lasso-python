"""solr_routes.py - Routes for Solr API."""

from fastapi import APIRouter

router = APIRouter(prefix="/solr", tags=["solr"])


# check solr health


@router.post("/testupload")
def testupload() -> dict:
    return {"message": "Test upload route"}


@router.get("/testdocs")
def testdocs() -> dict:
    return {"message": "Test docs route"}


@router.get("/docs")
def get_document() -> dict:
    return {"message": "Get document route"}


@router.post("/add")
def upload_file() -> dict:
    return {"message": "Upload file route"}


@router.get("/fetch")
def fetch_data():
    return {"message": "Fetch data route"}
