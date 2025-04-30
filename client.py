import argparse
import requests
import grpc
import os
import sys
import json
import base64
from datetime import datetime
from generated import image_cms_pb2
from generated import image_cms_pb2_grpc

def upload_image(image_path, title, author, tags, rest_port):
    """Upload a single image using REST API"""
    base_url = f"http://localhost:{rest_port}/api/v1"
    
    # Prepare form data
    form_data = {
        'title': title,
        'author': author,
        'tags': tags
    }
    
    # Upload the file
    try:
        with open(image_path, 'rb') as img_file:
            files = {'image_file': img_file}
            response = requests.post(
                f"{base_url}/images",
                data=form_data,
                files=files
            )
        
        if response.status_code == 201:
            image_data = response.json()
            print(f"Successfully uploaded image!")
            print(f"ID: {image_data['id']}")
            print(f"Title: {image_data['title']}")
            print(f"Tags: {', '.join(image_data['tags'])}")
            return True
        else:
            print(f"Failed to upload image: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return False

def list_images(rest_port, author=None, tags=None):
    """List images with optional filters using REST API"""
    base_url = f"http://localhost:{rest_port}/api/v1"
    
    # Build query parameters
    params = {}
    if author:
        params['author'] = author
    if tags:
        params['tags'] = tags
    
    try:
        # Make the request
        response = requests.get(f"{base_url}/images", params=params)
        
        if response.status_code == 200:
            images = response.json()
            print("\nImages in the system:")
            if not images:
                print("No images found.")
            else:
                for i, img in enumerate(images, 1):
                    print(f"  {i}. ID: {img['id']} - {img['title']} (by {img.get('author', 'Unknown')}) - Tags: {', '.join(img['tags'])}")
                print(f"\nTotal: {len(images)} images")
            return images
        else:
            print(f"Failed to list images: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error listing images: {str(e)}")
        return None

def get_image_by_id(image_id, rest_port):
    """Get a single image by ID (F2)"""
    base_url = f"http://localhost:{rest_port}/api/v1"
    
    try:
        response = requests.get(f"{base_url}/images/{image_id}")
        
        if response.status_code == 200:
            image_data = response.json()
            print(f"\nImage details:")
            print(f"ID: {image_data['id']}")
            print(f"Title: {image_data['title']}")
            print(f"Author: {image_data.get('author', 'Unknown')}")
            print(f"Tags: {', '.join(image_data['tags'])}")
            print(f"Created at: {image_data['created_at']}")
            
            # Ask if user wants to save the image
            if image_data.get('image_base64'):
                save = input("Would you like to save the image? (y/n): ")
                if save.lower() == 'y':
                    filename = f"image_{image_data['id']}.jpg"
                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(image_data['image_base64']))
                    print(f"Image saved as {filename}")
            
            return image_data
        else:
            print(f"Failed to get image: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error getting image: {str(e)}")
        return None

def update_image(image_id, rest_port, title=None, author=None, tags=None):
    """Update an image's metadata (F3)"""
    base_url = f"http://localhost:{rest_port}/api/v1"
    
    # Prepare update data
    update_data = {}
    if title is not None:
        update_data['title'] = title
    if author is not None:
        update_data['author'] = author
    if tags is not None:
        # Convert comma-separated string to list if needed
        if isinstance(tags, str):
            update_data['tags'] = [t.strip() for t in tags.split(',')]
        else:
            update_data['tags'] = tags
    
    try:
        # Make the request
        response = requests.patch(
            f"{base_url}/images/{image_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            image_data = response.json()
            print(f"Successfully updated image!")
            print(f"ID: {image_data['id']}")
            print(f"Title: {image_data['title']}")
            print(f"Author: {image_data.get('author', 'Unknown')}")
            print(f"Tags: {', '.join(image_data['tags'])}")
            return True
        else:
            print(f"Failed to update image: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error updating image: {str(e)}")
        return False

def delete_image(image_id, rest_port):
    """Delete an image by ID (F4)"""
    base_url = f"http://localhost:{rest_port}/api/v1"
    
    try:
        response = requests.delete(f"{base_url}/images/{image_id}")
        
        if response.status_code == 204:
            print(f"Successfully deleted image with ID: {image_id}")
            return True
        else:
            print(f"Failed to delete image: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False

def export_images(grpc_port, output_dir="exports", author=None, tags=None):
    """Export all images with optional filters and save to files (F5)"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a gRPC channel and stub
    channel = grpc.insecure_channel(f"localhost:{grpc_port}")
    stub = image_cms_pb2_grpc.ImageExportServiceStub(channel)
    
    try:
        # Create request with filters
        request = image_cms_pb2.ExportRequest()
        if author:
            request.author_filter = author
        if tags:
            # Convert comma-separated string to list if needed
            if isinstance(tags, str):
                tag_list = [t.strip() for t in tags.split(',')]
            else:
                tag_list = tags
            request.tag_filter.extend(tag_list)
        
        # Stream images and save them
        print("\nExporting images...")
        count = 0
        metadata_file = os.path.join(output_dir, "metadata.json")
        metadata_list = []
        
        for image in stub.ExportImages(request):
            count += 1
            # Save image file
            image_filename = f"image_{image.id}.jpg"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image.image_content)
            
            # Convert timestamp to string
            timestamp = datetime.fromtimestamp(
                image.created_at.seconds + image.created_at.nanos / 1e9
            ).isoformat()
            
            # Create metadata entry
            metadata = {
                "id": image.id,
                "title": image.title,
                "author": image.author,
                "tags": list(image.tags),
                "created_at": timestamp,
                "filename": image_filename
            }
            metadata_list.append(metadata)
            
            print(f"  Exported {image.title} (ID: {image.id})")
        
        # Save metadata
        with open(metadata_file, "w") as f:
            json.dump(metadata_list, f, indent=2)
        
        if count == 0:
            print("No images found to export.")
        else:
            print(f"\nExported {count} images to {output_dir}")
            print(f"Metadata saved to {metadata_file}")
        
    finally:
        # Close the channel when done
        channel.close()

def upload_sample_images(rest_port):
    """Upload sample images from the sample directory"""
    # Define sample directory and check if it exists
    sample_dir = "samples"
    if not os.path.isdir(sample_dir):
        print(f"Sample directory '{sample_dir}' not found.")
        return False
    
    # Define sample images with metadata
    sample_images = [
        {
            "filename": "Sample_1.jpg",
            "title": "Sample Image 1",
            "author": "Photographer 1",
            "tags": "sample,landscape,water"
        },
        {
            "filename": "Sample_2.jpg",
            "title": "Sample Image 2",
            "author": "Photographer 1",
            "tags": "sample,bird,animal"
        },
        {
            "filename": "Sample_3.jpg",
            "title": "Sample Image 3",
            "author": "Photographer 2",
            "tags": "sample,person,sport"
        }
    ]
    success_count = 0
    
    print("\nUploading sample images:")
    for image_data in sample_images:
        filename = image_data["filename"]
        file_path = os.path.join(sample_dir, filename)
        
        if not os.path.isfile(file_path):
            print(f"Sample image '{filename}' not found in sample directory.")
            continue
        
        print(f"Uploading {filename}...")
        if upload_image(
            file_path,  
            image_data["title"], 
            image_data["author"],  
            image_data["tags"], 
            rest_port
        ):
            success_count += 1
    
    print(f"\nSuccessfully uploaded {success_count} of {len(sample_images)} sample images.")
    return success_count > 0

def parse_command(line):
    """Parse a command line respecting quoted strings"""
    tokens = []
    current_token = ""
    in_quotes = False
    quote_char = None
    
    for char in line:
        if char in ['"', "'"]:
            if not in_quotes:  # Start of quoted string
                in_quotes = True
                quote_char = char
            elif char == quote_char:  # End of quoted string
                in_quotes = False
                quote_char = None
            else:  
                current_token += char
        elif char.isspace() and not in_quotes:  # Space outside quotes
            if current_token:  
                tokens.append(current_token)
                current_token = ""
        else: 
            current_token += char
    
    if current_token:
        tokens.append(current_token)
    
    return tokens

def parse_args(args):
    """Parse command arguments in a more Pythonic way"""
    parsed = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--'):
            # Handle flags with values
            if i + 1 < len(args) and not args[i+1].startswith('--'):
                parsed[arg[2:]] = args[i+1]  # Store without the -- prefix
                i += 2
            else:
                # Handle boolean flags
                parsed[arg[2:]] = True
                i += 1
        else:
            # Handle positional arguments
            if 'positional' not in parsed:
                parsed['positional'] = []
            parsed['positional'].append(arg)
            i += 1
    return parsed

def interactive_cli():
    # Default ports
    rest_port = 8001
    grpc_port = 50051
    
    print("===== Image CMS Client =====")
    print("Type 'help' for available commands or 'exit' to quit.")
    
    while True:
        try:
            # Get command from user
            input_line = input("\n> ").strip()
            cmd = parse_command(input_line)
            
            if not cmd:
                continue
                
            command = cmd[0].lower()
            
            # Process command
            if command in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
                
            elif command == 'help':
                print("\nAvailable commands:")
                print("  list [--author \"<author>\"] [--tags <tags>]  - List all images with optional filters")
                print("  get <id>                                    - Get image by ID")
                print("  upload <file> \"<title>\" \"<author>\" <tags>   - Upload an image (use quotes for values with spaces)")
                print("  update <id> [--title \"<title>\"] [--author \"<author>\"] [--tags <tags>]")
                print("                                              - Update an image")
                print("  delete <id>                                 - Delete an image")
                print("  export [--author \"<author>\"] [--tags <tags>] [--dir <directory>]")
                print("                                              - Export images to files")
                print("  upload-samples                              - Upload sample images")
                print("  exit                                        - Exit the program")
                print("\nNote: Use quotes (\"\") for values containing spaces.")
                
            elif command == 'list':
                # Parse arguments
                args = parse_args(cmd[1:])
                author = args.get('author')
                tags = args.get('tags')
                
                list_images(rest_port, author, tags)
                            
            elif command == 'get':
                if len(cmd) < 2:
                    print("Error: Missing image ID.")
                    print("Usage: get <id>")
                    continue
                
                try:
                    image_id = int(cmd[1])
                    get_image_by_id(image_id, rest_port)
                except ValueError:
                    print("Error: Image ID must be an integer.")
                
            elif command == 'upload':
                if len(cmd) < 5:
                    print("Error: Missing arguments.")
                    print("Usage: upload <file> <title> <author> <tags>")
                    print("Use quotes for values containing spaces: upload image.jpg \"My Title\" \"John Doe\" \"tag1,tag2\"")
                    continue
                    
                image_path = cmd[1]
                title = cmd[2]
                author = cmd[3]
                tags = cmd[4]
                
                upload_image(image_path, title, author, tags, rest_port)
                
            elif command == 'update':
                if len(cmd) < 2:
                    print("Error: Missing image ID.")
                    print("Usage: update <id> [--title <title>] [--author <author>] [--tags <tags>]")
                    continue
                
                try:
                    image_id = int(cmd[1])
                    title = None
                    author = None
                    tags = None
                    
                    args = parse_args(cmd[2:])
                    title = args.get('title')
                    author = args.get('author')
                    tags = args.get('tags')
                    
                    if title is None and author is None and tags is None:
                        print("Error: No update parameters provided.")
                        print("Usage: update <id> [--title <title>] [--author <author>] [--tags <tags>]")
                        continue
                    
                    update_image(image_id, rest_port, title, author, tags)
                    
                except ValueError:
                    print("Error: Image ID must be an integer.")
                
            elif command == 'delete':
                if len(cmd) < 2:
                    print("Error: Missing image ID.")
                    print("Usage: delete <id>")
                    continue
                
                try:
                    image_id = int(cmd[1])
                    
                    # Ask for confirmation
                    confirm = input(f"Are you sure you want to delete image {image_id}? (y/n): ")
                    if confirm.lower() == 'y':
                        delete_image(image_id, rest_port)
                    else:
                        print("Delete operation cancelled.")
                        
                except ValueError:
                    print("Error: Image ID must be an integer.")
                
            elif command == 'export':
                # Parse arguments
                args = parse_args(cmd[1:])
                author = args.get('author')
                tags = args.get('tags')
                output_dir = args.get('dir', "exports")
                
                export_images(grpc_port, output_dir, author, tags)
                
            elif command == 'upload-samples':
                upload_sample_images(rest_port)

            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def setup_parsers():
    """Set up command parsers using argparse"""
    parser = argparse.ArgumentParser(description="Image CMS Client")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List images")
    list_parser.add_argument("--author", help="Filter by author")
    list_parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    
    # Export command 
    export_parser = subparsers.add_parser("export", help="Export images")
    export_parser.add_argument("--author", help="Filter by author")
    export_parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    export_parser.add_argument("--dir", default="exports", help="Output directory")

    return parser

if __name__ == "__main__":
    # Parse command line arguments for initial configuration
    parser = argparse.ArgumentParser(description="Image CMS Client")
    parser.add_argument("--rest-port", type=int, default=8001,
                        help="Initial REST API port (default: 8001)")
    parser.add_argument("--grpc-port", type=int, default=50051,
                        help="Initial gRPC server port (default: 50051)")
    
    args = parser.parse_args()
    interactive_cli()
