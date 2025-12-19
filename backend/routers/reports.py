"""
Router para endpoints de reportes ciudadanos.

Endpoints:
- POST /reports: crear nuevo reporte
- GET /reports: listar reportes con filtros opcionales
- DELETE /reports/{report_id}: eliminar un reporte
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from backend.database import get_db
from backend.models import UserReport
from backend.schemas import UserReportCreate, UserReportRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=UserReportRead, status_code=201)
def create_report(
    report: UserReportCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo reporte ciudadano.
    
    Valida coordenadas (CDMX) y guarda en la base de datos.
    """
    db_report = UserReport(
        tipo=report.tipo,
        descripcion=report.descripcion,
        lat=report.lat,
        lon=report.lon,
        alcaldia=report.alcaldia,
        colonia=report.colonia
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("", response_model=List[UserReportRead])
def get_reports(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de incidente"),
    alcaldia: Optional[str] = Query(None, description="Filtrar por alcaldía"),
    colonia: Optional[str] = Query(None, description="Filtrar por colonia"),
    limit: int = Query(200, ge=1, le=1000, description="Límite de resultados"),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de reportes ciudadanos con filtros opcionales.
    
    Ordenados por fecha de creación descendente.
    """
    query = db.query(UserReport)
    
    if tipo:
        query = query.filter(UserReport.tipo == tipo)
    if alcaldia:
        query = query.filter(UserReport.alcaldia == alcaldia)
    if colonia:
        query = query.filter(UserReport.colonia == colonia)
    
    reports = query.order_by(UserReport.created_at.desc()).limit(limit).all()
    return reports


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """
    Elimina un reporte ciudadano.
    
    Retorna 204 si se elimina exitosamente, 404 si no existe.
    """
    db_report = db.query(UserReport).filter(UserReport.id == report_id).first()
    
    if not db_report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    db.delete(db_report)
    db.commit()
    return None

