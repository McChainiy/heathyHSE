from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, DateTime, ForeignKey, String
from db.db import Base
import datetime

class UserLog(Base):
    __tablename__ = "user_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, 
                                                          default=datetime.datetime.now,
                                                          nullable=False)

    today_water: Mapped[float] = mapped_column(Float, default=0.0)
    today_calories: Mapped[float] = mapped_column(Float, default=0.0)
    
    action: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, default=0.0, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="user_log")