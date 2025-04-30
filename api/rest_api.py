from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Query
from typing import Optional, List, Dict, Any
import base64
from services.image_service import ImageService
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()
image_service = ImageService()

# Pydantic models 
class ImageListResponseItem(BaseModel):
    """Response model for basic image information"""
    id: int
    title: str
    author: Optional[str] = None
    tags: List[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

class ImageResponse(BaseModel):
    """Response model for complete image information"""
    id: int
    title: str
    author: Optional[str] = None
    tags: List[str]
    created_at: datetime
    image_base64: Optional[str] = None
    
    class Config:
        orm_mode = True

class ImageUpdate(BaseModel):
    """Request model for updating images"""
    title: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None

@app.get("/api/v1/images", response_model=List[ImageListResponseItem])
def get_images(
    author: Optional[str] = Query(None, description="Filter by author"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)")
):
    """List images with optional filtering"""
    # Convert comma-separated tags to list 
    tag_list = None
    if tags:
        tag_list = tags.split(',')
        
    images = image_service.get_images(author=author, tags=tag_list)
    
    # Format the response
    result = []
    for img in images:
        result.append(ImageListResponseItem(
            id=img.id,
            title=img.title,
            author=img.author,
            tags=[tag.name for tag in img.tags],
            created_at=img.created_at
        ))
    return result

@app.post("/api/v1/images", response_model=ImageResponse, status_code=201)
async def create_image(
    title: str = Form(...),
    author: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    image_file: UploadFile = File(...)
):
    """Create a new image with metadata"""
    # Split tags
    tag_list = []
    if tags:
        tag_list = tags.split(',')
    
    # Get image content
    image_content = await image_file.read()
    
    # Add to database using the global service
    db_image = image_service.create_new_image(
        title=title,
        author=author,
        image_blob=image_content,
        tag_names=tag_list
    )
    
    # Prepare response
    tags_response = [tag.name for tag in db_image.tags]
    image_base64 = None
    if db_image.image_blob:
        image_base64 = base64.b64encode(db_image.image_blob).decode('utf-8')
    
    return ImageResponse(
        id=db_image.id,
        title=db_image.title,
        author=db_image.author,
        tags=tags_response,
        created_at=db_image.created_at,
        image_base64=image_base64
    )

@app.get("/api/v1/images/{image_id}", response_model=ImageResponse)
def get_image(image_id: int):
    """Get a single image by ID with all details"""
    db_image = image_service.get_image_by_id(image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Convert image to base64 for response
    image_base64 = None
    if db_image.image_blob:
        image_base64 = base64.b64encode(db_image.image_blob).decode('utf-8')
    
    return ImageResponse(
        id=db_image.id,
        title=db_image.title,
        author=db_image.author,
        tags=[tag.name for tag in db_image.tags],
        created_at=db_image.created_at,
        image_base64=image_base64
    )

@app.patch("/api/v1/images/{image_id}", response_model=ImageResponse)
def update_image(image_id: int, update_data: ImageUpdate):
    """Update an existing image's metadata"""
    updated_image = image_service.update_image(
        image_id=image_id,
        title=update_data.title,
        author=update_data.author,
        tag_names=update_data.tags
    )
    
    if not updated_image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_base64 = None
    if updated_image.image_blob:
        image_base64 = base64.b64encode(updated_image.image_blob).decode('utf-8')
    
    return ImageResponse(
        id=updated_image.id,
        title=updated_image.title,
        author=updated_image.author,
        tags=[tag.name for tag in updated_image.tags],
        created_at=updated_image.created_at,
        image_base64=image_base64
    )

@app.delete("/api/v1/images/{image_id}", status_code=204)
def delete_image(image_id: int):
    """Delete an image by ID"""
    success = image_service.delete_image_by_id(image_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    