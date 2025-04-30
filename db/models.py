from sqlalchemy import Column, Integer, String, LargeBinary, TIMESTAMP, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import database

# Association Table for Many-to-Many between Image and Tag
image_tags_association = Table('image_tags', database.Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Image(database.Base):
    """SQLAlchemy model for image blob and metadata"""
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    image_blob = Column(LargeBinary, nullable=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    tags = relationship("Tag", secondary=image_tags_association, back_populates="images")

class Tag(database.Base):
    """SQLAlchemy model for image tags"""
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    images = relationship("Image", secondary=image_tags_association, back_populates="tags")