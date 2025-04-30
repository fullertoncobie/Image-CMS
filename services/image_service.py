from typing import List, Optional, Generator
from db.repository import Repository

class ImageService:
    """Service layer for image operations using repository pattern"""
    
    def __init__(self):
        # Create the repository
        self.repository = Repository()
    
    def get_images(self, author: Optional[str] = None, 
                  tags: Optional[List[str]] = None, 
                  skip: int = 0, limit: int = 100):
        """Get images with optional filtering"""
        return self.repository.get_all(author=author, tags=tags, skip=skip, limit=limit)
    
    def get_image_by_id(self, image_id: int):
        """Get a single image by ID"""
        return self.repository.get_by_id(image_id)
    
    def create_new_image(self, title: str, author: str, 
                        image_blob: bytes, tag_names: List[str]):
        """Create a new image with tags"""
        data = {
            'title': title,
            'author': author,
            'image_blob': image_blob,
            'tag_names': tag_names
        }
        return self.repository.create(data)
            
    def update_image(self, image_id: int, 
                    title: Optional[str] = None, 
                    author: Optional[str] = None,
                    tag_names: Optional[List[str]] = None):
        """Update an image's metadata"""
        # Only include fields that are provided
        data = {}
        if title is not None:
            data['title'] = title
        if author is not None:
            data['author'] = author
        if tag_names is not None:
            data['tag_names'] = tag_names
            
        return self.repository.update(image_id, data)
            
    def delete_image_by_id(self, image_id: int) -> bool:
        """Delete an image by ID"""
        return self.repository.delete(image_id)
            
    def stream_export_data(self, author_filter: Optional[str] = None,
                          tag_filter: Optional[List[str]] = None) -> Generator:
        """Stream images for export"""
        return self.repository.stream_all(author=author_filter, tags=tag_filter)