import grpc
from concurrent import futures
from typing import Dict, Any
from google.protobuf.timestamp_pb2 import Timestamp
import generated.image_cms_pb2 as image_cms_pb2
import generated.image_cms_pb2_grpc as image_cms_pb2_grpc
from services.image_service import ImageService

# Global service instance
image_service = ImageService()

def model_to_image_message(img):
    """Convert DB model to protobuf message"""
    message = image_cms_pb2.ImageMessage()
    message.id = str(img.id)
    message.image_content = img.image_blob or b''
    message.title = img.title
    message.author = img.author or ""
    message.tags.extend([tag.name for tag in img.tags])
    
    # Set timestamp
    ts = Timestamp()
    ts.FromDatetime(img.created_at)
    message.created_at.CopyFrom(ts)
    
    return message

class ImageExportServicer(image_cms_pb2_grpc.ImageExportServiceServicer):
    """gRPC service implementation for image exports"""

    def ExportImages(self, request, context):
        """Stream images to client based on filters"""
        print(f"gRPC export request: author='{request.author_filter}', tags={list(request.tag_filter)}")
        
        try:
            # Get data as generator - use the global service directly
            image_gen = image_service.stream_export_data(
                author_filter=request.author_filter or None,
                tag_filter=list(request.tag_filter) or None
            )

            # Stream results back to client
            for img in image_gen:
                yield model_to_image_message(img)

        except Exception as e:
            print(f"Error in ExportImages: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Server error: {e}")

def create_grpc_server():
    """Create and configure the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_cms_pb2_grpc.add_ImageExportServiceServicer_to_server(
        ImageExportServicer(), server
    )
    return server