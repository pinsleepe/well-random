from database import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer)

engine = db.engine

Base = declarative_base()
Base.metadata.create_all(engine)


class ArmAssigment(Base):
    __tablename__ = "arm_assigment"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    orientation = Column(
        Integer,
        nullable=False
    )
    gender = Column(
        Integer,
        nullable=False
    )
    partnership = Column(
        Integer,
        nullable=False
    )
    health = Column(
        Integer,
        nullable=False
    )
    arm = Column(
        Integer,
        nullable=False
    )


if __name__ == "__main__":
    Base.metadata.create_all(engine,
                             Base.metadata.tables.values(),
                             checkfirst=True)
