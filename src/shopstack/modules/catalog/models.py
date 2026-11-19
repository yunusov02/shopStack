# id, tenant_id, name text, price numeric(14,2) CHECK (price >= 0)
import uuid
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column

from shopstack.db.base import Base


class Catalog(Base):
    __tablename__ = "catalog"

    tenant_id: Mapped[uuid.UUID] = mapped_column("tenant_id")
    name: Mapped[str] = mapped_column("name")
    text: Mapped[str] = mapped_column("text")
    price: Mapped[Decimal] = mapped_column("price")

