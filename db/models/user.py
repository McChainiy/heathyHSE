from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Date, ForeignKey
from db.db import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  

    weight: Mapped[float | None] = mapped_column(Float)
    height: Mapped[float | None] = mapped_column(Float)
    age: Mapped[int | None] = mapped_column(Integer)
    activity: Mapped[int | None] = mapped_column(Integer) 
    city: Mapped[str | None] = mapped_column(String(100))

    water_goal: Mapped[float | None] = mapped_column(Float)
    calorie_goal: Mapped[float | None] = mapped_column(Float)

    logged_water: Mapped[float | None] = mapped_column(Float, default=0.0)
    added_water: Mapped[float | None] = mapped_column(Float, default=0.0, nullable=True)

    logged_calories: Mapped[float | None] = mapped_column(Float, default=0.0)
    burned_calories: Mapped[float | None] = mapped_column(Float, default=0.0)


    cur_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    history: Mapped[list["UserHistory"]] = relationship(
        "UserHistory", back_populates="user", cascade="all, delete-orphan"
    )
    user_log: Mapped[list["UserLog"]] = relationship(
        "UserLog", back_populates="user", cascade="all, delete-orphan"
    )