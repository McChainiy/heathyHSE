from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, Date, ForeignKey
from db.db import Base
import datetime



class UserHistory(Base):
    __tablename__ = "user_history"

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), primary_key=True)
    date: Mapped[datetime.date] = mapped_column(primary_key=True)

    water_goal: Mapped[float | None] = mapped_column(Float)
    calorie_goal: Mapped[float | None] = mapped_column(Float)
    logged_water: Mapped[float] = mapped_column(Float, default=0.0)
    logged_calories: Mapped[float] = mapped_column(Float, default=0.0)
    burned_calories: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["User"] = relationship("User", back_populates="history")
