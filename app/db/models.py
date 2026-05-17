from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    cik: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    quarters: Mapped[list[Quarter]] = relationship(back_populates="company")


class Quarter(Base):
    __tablename__ = "quarters"
    __table_args__ = (UniqueConstraint("company_id", "fiscal_year", "fiscal_quarter"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"))
    fiscal_year: Mapped[int] = mapped_column(Integer)
    fiscal_quarter: Mapped[int] = mapped_column(Integer)
    period_end: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    company: Mapped[Company] = relationship(back_populates="quarters")
    filings: Mapped[list[Filing]] = relationship(back_populates="quarter")
    metrics: Mapped[list[Metric]] = relationship(back_populates="quarter")


class Filing(Base):
    __tablename__ = "filings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    quarter_id: Mapped[str] = mapped_column(ForeignKey("quarters.id"))
    kind: Mapped[str] = mapped_column(String(16))
    source: Mapped[str] = mapped_column(String(16))
    sha256: Mapped[str] = mapped_column(String(64))
    raw_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    quarter: Mapped[Quarter] = relationship(back_populates="filings")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    quarter_id: Mapped[str] = mapped_column(ForeignKey("quarters.id"))
    name: Mapped[str] = mapped_column(String(64))
    value: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    unit: Mapped[str] = mapped_column(String(32))
    source_filing_id: Mapped[str] = mapped_column(ForeignKey("filings.id"))

    quarter: Mapped[Quarter] = relationship(back_populates="metrics")
