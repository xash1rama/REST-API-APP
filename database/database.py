from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv("../.env")


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@postgres:5432/{DB_NAME}"


engine = create_async_engine(DB_URL, echo=True)
session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    coordinate_long = Column(Float, nullable=False)
    coordinate_lat = Column(Float, nullable=False)

    activities = relationship(
        "Activity",
        back_populates="activity_build",
        foreign_keys="[Activity.activity_build_id]",
        lazy="selectin",
    )

    organizations = relationship(
        "Organization",
        back_populates="organization_build",
        foreign_keys="[Organization.build]",
        lazy="selectin",
    )


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)
    activity_build_id = Column(Integer, ForeignKey("builds.id"), nullable=True)

    subactivities = relationship("Activity", backref="parent", remote_side=[id], lazy="selectin")

    activity_build = relationship(
        "Build",
        back_populates="activities",
        foreign_keys=[activity_build_id],
        lazy="selectin",
    )

    activity_orgs = relationship(
        "Organization",
        back_populates="orgs_activities",
        foreign_keys="[Organization.activities_id]",
        lazy="selectin",
    )

    def get_depth(self):
        """Возвращает уровень вложенности"""
        depth = 0
        current_activity = self
        while current_activity.parent:
            depth += 1
            current_activity = current_activity.parent
        return depth

    def can_add_subactivity(self):
        return self.get_depth() < 3


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    number_phone = Column(ARRAY(String), nullable=False)
    build = Column(Integer, ForeignKey("builds.id"), nullable=False)
    activities_id = Column(Integer, ForeignKey("activities.id"))

    organization_build = relationship(
        "Build",
        back_populates="organizations",
        foreign_keys="[Organization.build]",
        lazy="selectin",
    )

    orgs_activities = relationship(
        "Activity",
        back_populates="activity_orgs",
        foreign_keys="[Organization.activities_id]",
        lazy="selectin",
    )

