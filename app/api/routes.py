from datetime import datetime, timedelta, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models, schemas
from app.core.auth import get_current_user, require_admin
from fastapi import Body, Request
from app.services import auth_service, rate_limit, notifications
from app.core.config import get_settings
from app.api import imports as imports_router

router = APIRouter()
router.include_router(imports_router.router, prefix="/imports", tags=["imports"])


@router.get("/")
def api_root():
    return {"message": "API v1: use /requests e endpoints relacionados"}


@router.get("/meta")
def meta(user=Depends(get_current_user)):
    settings = get_settings()
    return {
        "allowed_services": settings.allowed_services,
        "allowed_regions": settings.allowed_regions,
        "allowed_accounts": settings.allowed_accounts,
        "max_expiration_days": settings.max_expiration_days,
    }

@router.get("/requests/summary")
def requests_summary(db: Session = Depends(get_db), admin=Depends(require_admin)):
    today = date.today()
    in_7 = today + timedelta(days=7)
    in_30 = today + timedelta(days=30)
    expiring_7 = (
        db.query(models.request.Request)
        .filter(models.request.Request.status.in_(["pendente", "aprovado"]))
        .filter(models.request.Request.expires_at >= today)
        .filter(models.request.Request.expires_at <= in_7)
        .count()
    )
    expiring_30 = (
        db.query(models.request.Request)
        .filter(models.request.Request.status.in_(["pendente", "aprovado"]))
        .filter(models.request.Request.expires_at >= today)
        .filter(models.request.Request.expires_at <= in_30)
        .count()
    )
    expired_unremoved = (
        db.query(models.request.Request)
        .filter(models.request.Request.status == "expirado")
        .count()
    )
    pending = db.query(models.request.Request).filter(models.request.Request.status == "pendente").count()
    return {
        "expiring_7": expiring_7,
        "expiring_30": expiring_30,
        "expired_unremoved": expired_unremoved,
        "pending": pending,
    }


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(payload: LoginPayload, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    if not rate_limit.allow(f"login:{ip}"):
        raise HTTPException(status_code=429, detail="Muitas tentativas, aguarde um pouco")
    user = auth_service.get_user_by_username(db, payload.username)
    if not user or not auth_service.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access, refresh = auth_service.create_tokens(user)
    return {"access_token": access, "refresh_token": refresh, "user": {"username": user.username, "role": user.role, "display_name": user.display_name}}


@router.post("/auth/refresh")
def refresh(token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        payload = auth_service.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(models.user.User).filter(models.user.User.id == payload.get("sub")).first()
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="User inactive")
    access, refresh_token = auth_service.create_tokens(user)
    return {"access_token": access, "refresh_token": refresh_token}


@router.post("/auth/users", dependencies=[Depends(require_admin)])
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        created = auth_service.create_user(db, user_in.username, user_in.password, user_in.role, user_in.display_name)
        return {"username": created.username, "role": created.role, "display": created.display_name}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/auth/users", response_model=List[schemas.User], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.user.User).all()


class RemovePayload(BaseModel):
    remover: str


@router.post("/requests", response_model=schemas.Request)
def create_request(
    request_in: schemas.RequestCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins não podem criar solicitações")
    settings = get_settings()
    today = date.today()
    if request_in.expires_at:
        if request_in.expires_at <= today:
            raise HTTPException(status_code=400, detail="Data de remoção deve ser futura")
        max_date = today + timedelta(days=settings.max_expiration_days)
        if request_in.expires_at > max_date:
            raise HTTPException(status_code=400, detail=f"Data de remoção não pode exceder {settings.max_expiration_days} dias")
    if request_in.retention_days is not None and request_in.retention_days < 1:
        raise HTTPException(status_code=400, detail="Tempo de uso (dias) deve ser positivo")
    if request_in.flow_type not in ("finops", "outros"):
        raise HTTPException(status_code=400, detail="flow_type deve ser 'finops' ou 'outros'")
    if request_in.flow_type == "finops":
        if request_in.service_type not in settings.allowed_services:
            raise HTTPException(status_code=400, detail=f"Serviço não permitido. Permitidos: {', '.join(settings.allowed_services)}")
        if request_in.region not in settings.allowed_regions:
            raise HTTPException(status_code=400, detail=f"Região não permitida. Permitidas: {', '.join(settings.allowed_regions)}")
        if not request_in.aws_account:
            raise HTTPException(status_code=400, detail="Conta AWS é obrigatória")
        if settings.allowed_accounts:
            if request_in.aws_account not in settings.allowed_accounts:
                raise HTTPException(status_code=400, detail=f"Conta não permitida. Permitidas: {', '.join(settings.allowed_accounts)}")
        if not request_in.change_type:
            raise HTTPException(status_code=400, detail="Tipo de mudança é obrigatório")
        if not request_in.justification:
            raise HTTPException(status_code=400, detail="Justificativa é obrigatória")
        if not request_in.criticality:
            raise HTTPException(status_code=400, detail="Criticidade é obrigatória")
    else:
        # fluxo "outros": não força catálogos de serviço/região/conta; define serviço como "outro" se vier vazio
        if not request_in.service_type:
            request_in.service_type = "outro"
    data = request_in.dict()
    data["requester"] = user.display_name or user.username
    obj = models.request.Request(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _add_audit(db, obj.id, "created", user.username)
    notifications.send_webhook(_fmt_webhook("Nova", obj, actor=user.username))
    return obj


@router.get("/requests")
def list_requests(
    status: Optional[str] = None,
    requester: Optional[str] = None,
    id: Optional[str] = None,
    aws_account: Optional[str] = None,
    expires_before: Optional[date] = None,
    expires_after: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    q = db.query(models.request.Request)
    if user.role != "admin":
        q = q.filter(models.request.Request.requester == (user.display_name or user.username))
    else:
        if id:
            q = q.filter(models.request.Request.id.ilike(f"%{id}%"))
        if aws_account:
            q = q.filter(models.request.Request.aws_account.ilike(f"%{aws_account}%"))
        if status:
            q = q.filter(models.request.Request.status == status)
        if requester:
            q = q.filter(models.request.Request.requester == requester)
    if expires_before:
        q = q.filter(models.request.Request.expires_at <= expires_before)
    if expires_after:
        q = q.filter(models.request.Request.expires_at >= expires_after)
    total = q.count()
    items = (
        q.order_by(models.request.Request.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.patch("/requests/{request_id}", response_model=schemas.Request)
def update_request(
    request_id: str,
    request_in: schemas.RequestUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    obj = db.query(models.request.Request).filter(models.request.Request.id == request_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    data = request_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(obj, field, value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _add_audit(db, obj.id, "updated", admin.username)
    notifications.send_webhook(_fmt_webhook(f"Status: {obj.status}", obj, actor=admin.username))
    return obj


@router.post("/requests/{request_id}/expire", response_model=schemas.Request)
def expire_request(request_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    obj = db.query(models.request.Request).filter(models.request.Request.id == request_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    obj.status = "expirado"
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _add_audit(db, obj.id, "expired", admin.username)
    notifications.send_webhook(_fmt_webhook("Expirado", obj, actor=admin.username))
    return obj


@router.post("/requests/{request_id}/mark-removed", response_model=schemas.Request)
def mark_removed(
    request_id: str,
    payload: RemovePayload,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    obj = db.query(models.request.Request).filter(models.request.Request.id == request_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    obj.status = "removido"
    obj.last_alert_at = datetime.utcnow()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _add_audit(db, obj.id, "removed", admin.username)
    notifications.send_webhook(_fmt_webhook("Removido", obj, actor=admin.username))
    return obj


@router.delete("/requests/{request_id}", status_code=204)
def delete_request(
    request_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = db.query(models.request.Request).filter(models.request.Request.id == request_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    is_owner = obj.requester == (user.display_name or user.username)
    if not (user.role == "admin" or is_owner):
        raise HTTPException(status_code=403, detail="Sem permissão para remover esta solicitação")
    db.query(models.audit.Audit).filter(models.audit.Audit.request_id == obj.id).delete()
    db.delete(obj)
    db.commit()
    notifications.send_webhook(f"[Removido definitivamente] {request_id} por {user.username}")
    return {"detail": "deleted"}


def _fmt_webhook(event: str, req: models.request.Request, actor: str) -> str:
    cost = f" • Custo prev: {req.estimated_cost}" if req.estimated_cost else ""
    return (
        f"[GMUD] {event} | {req.service_type} • conta {req.aws_account or '-'} • região {req.region or '-'}\n"
        f"Tipo: {req.change_type or '-'} • Criticidade: {req.criticality or '-'}\n"
        f"Solicitante: {req.requester} • Ação por: {actor}\n"
        f"Justificativa: {req.justification or '-'}{cost}\n"
        f"Expira em: {req.expires_at}"
    )


def _add_audit(db: Session, request_id: str, action: str, by: str):
    audit = models.audit.Audit(request_id=request_id, action=action, by=by, details=None)
    db.add(audit)
    db.commit()
    db.refresh(audit)
