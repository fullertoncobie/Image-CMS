from abc import ABC, abstractmethod
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Generator, Any, Dict
from db import models
from db.database import get_db_session

# Interface
class ImageRepository(ABC):
    """Interface for image data access operations"""
    
    @abstractmethod
    def get_all(self, author: Optional[str] = None, 
               tags: Optional[List[str]] = None, 
               skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all images with optional filtering"""
        pass
    
    @abstractmethod
    def get_by_id(self, image_id: int) -> Optional[Any]:
        """Get a single image by ID"""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        """Create a new image"""
        pass
    
    @abstractmethod
    def update(self, image_id: int, data: Dict[str, Any]) -> Optional[Any]:
        """Update an existing image"""
        pass
    
    @abstractmethod
    def delete(self, image_id: int) -> bool:
        """Delete an image"""
        pass
    
    @abstractmethod
    def stream_all(self, author: Optional[str] = None,
                  tags: Optional[List[str]] = None) -> Generator[Any, None, None]:
        """Stream all images for efficient processing"""
        pass

# Concrete implementation
class Repository(ImageRepository):
    """SQLAlchemy implementation of the image repository"""
    
    def get_all(self, author: Optional[str] = None, 
               tags: Optional[List[str]] = None, 
               skip: int = 0, limit: int = 100) -> List[models.Image]:
        """Get all images with optional filtering"""
        db = get_db_session()
        try:
            # Use joinedload to eagerly load tags
            query = db.query(models.Image).options(joinedload(models.Image.tags))
            
            # Filter by author if provided
            if author:
                query = query.filter(models.Image.author == author)
                
            # Filter by tags if provided
            if tags:
                query = query.join(models.image_tags_association).join(models.Tag)
                query = query.filter(models.Tag.name.in_(tags))
                query = query.distinct()  # Avoid duplicates

            # Execute query within session
            images = query.offset(skip).limit(limit).all()
            
            # Load tags and detach from session
            for image in images:
                _ = [tag.name for tag in image.tags]  # Force load tags
                db.expunge(image)
                
            return images
        finally:
            db.close()
    
    def get_by_id(self, image_id: int) -> Optional[models.Image]:
        """Get a single image by ID"""
        db = get_db_session()
        try:
            # Use joinedload to eagerly load the tags relationship
            image = db.query(models.Image).options(
                joinedload(models.Image.tags)
            ).filter(models.Image.id == image_id).first()
            
            if image:
                _ = [tag.name for tag in image.tags]  # Force load tags
                db.expunge(image)
                
            return image
        finally:
            db.close()
    
    def create(self, data: Dict[str, Any]) -> models.Image:
        """Create a new image with tags"""
        db = get_db_session()
        try:
            # Extract data
            title = data['title']
            author = data.get('author')
            image_blob = data['image_blob']
            tag_names = data.get('tag_names', [])
            
            # Handle tags
            tags = []
            for tag_name in tag_names:
                tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
                if not tag:
                    tag = models.Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                tags.append(tag)
            
            # Create the image
            db_image = models.Image(
                title=title,
                author=author,
                image_blob=image_blob,
                tags=tags
            )
            
            db.add(db_image)
            db.commit()
            db.refresh(db_image)
            
            # Force load tags before detaching
            _ = [tag.name for tag in db_image.tags]
            db.expunge(db_image)
            
            return db_image
        finally:
            db.close()
            
    def update(self, image_id: int, data: Dict[str, Any]) -> Optional[models.Image]:
        """Update an image's metadata"""
        db = get_db_session()
        try:
            # Get the image first
            db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
            
            if not db_image:
                return None
                
            # Update fields if provided
            if 'title' in data:
                db_image.title = data['title']
                
            if 'author' in data:
                db_image.author = data['author']
                
            # Update tags if provided
            if 'tag_names' in data:
                # Clear existing tags
                db_image.tags = []
                
                # Add new tags
                for tag_name in data['tag_names']:
                    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
                    if not tag:
                        tag = models.Tag(name=tag_name)
                        db.add(tag)
                        db.flush()
                    db_image.tags.append(tag)
            
            # Save changes
            db.commit()
            db.refresh(db_image)
            
            # Force load tags before detaching
            _ = [tag.name for tag in db_image.tags]
            db.expunge(db_image)
            
            return db_image
        finally:
            db.close()
            
    def delete(self, image_id: int) -> bool:
        """Delete an image by ID"""
        db = get_db_session()
        try:
            db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
            
            if not db_image:
                return False
                
            db.delete(db_image)
            db.commit()
            return True
        finally:
            db.close()
            
    def stream_all(self, author: Optional[str] = None,
                  tags: Optional[List[str]] = None) -> Generator[models.Image, None, None]:
        """Stream images for export"""
        db = get_db_session()
        try:
            # Use eager loading for tags
            query = db.query(models.Image).options(joinedload(models.Image.tags))
            
            if author:
                query = query.filter(models.Image.author == author)
                
            if tags:
                query = query.join(models.image_tags_association).join(models.Tag)
                query = query.filter(models.Tag.name.in_(tags))
                query = query.distinct()
            
            # Stream results in batches
            batch_size = 100
            offset = 0
            
            while True:
                batch = query.offset(offset).limit(batch_size).all()
                if not batch:
                    break
                    
                for image in batch:
                    # Force load tags before yielding
                    tag_name = [tag.name for tag in image.tags]
                    yield image
                    
                offset += batch_size
        finally:
            db.close()