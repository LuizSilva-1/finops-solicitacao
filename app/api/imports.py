import csv
import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models, schemas
from app.core.auth import require_admin
from app.core.config import get_settings

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/csv", response_model=schemas.ImportResult)
def import_csv(file: UploadFile, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Envie um arquivo CSV")
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    created: List[str] = []
    settings = get_settings()
    for row in reader:
        try:
            service_type = row.get("service_type")
            if service_type not in settings.allowed_services:
                raise ValueError("service_type não permitido")
            region = row.get("region")
            if region not in settings.allowed_regions:
                raise ValueError("region não permitida")
            expires_at = datetime.strptime(row["expires_at"], "%Y-%m-%d").date()
            obj = models.request.Request(
                requester=row.get("requester") or admin.username,
                service_type=service_type,
                aws_account=row.get("aws_account"),
                region=region,
                expires_at=expires_at,
                status=row.get("status", "pendente"),
                params=row.get("params"),
                tags=row.get("tags"),
            )
            db.add(obj)
            db.flush()
            created.append(obj.id)
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Erro na linha {reader.line_num}: {exc}")
    db.commit()
    return {"created": created, "count": len(created)}
