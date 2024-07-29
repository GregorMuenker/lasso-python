"""nexus_routes.py - Routes for the Nexus API."""

from fastapi import APIRouter

router = APIRouter(prefix="nexus/", tags=["nexus"])
