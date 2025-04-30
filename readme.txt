## Prerequisites
A `requirements.txt` file is included. Install the necessary dependencies by running:
```bash
pip install -r requirements.txt

Server Setup 
To set up the server, run main.py. This script will:
    Create the necessary database.
    Establish servers for both REST and gRPC APIs.
    Initialize other relevant infrastructure.
You can specify optional ports for the REST and gRPC servers. If not provided, default ports will be used.

python main.py [--rest-port PORT] [--grpc-port PORT]

Client Usage
A sample Command Line Interface (CLI) client (client.py) is provided for interacting with the server. By default, it connects to the server's default ports, but you can specify different ports using optional arguments:

python client.py [--rest-port PORT] [--grpc-port PORT]

CLI Commands
The client supports the following commands:
    List all images with optional filters:
    list [--author "<author>"] [--tags <tags>]

    Get image by ID:
    get <id>

    Upload an image: (Use quotes for values with spaces)
    upload <file> "<title>" "<author>" <tags>

    Update an image:
    update <id> [--title "<title>"] [--author "<author>"] [--tags <tags>]

    Delete an image:
    delete <id>

    Export images to files:
    export [--author "<author>"] [--tags <tags>] [--dir <directory>]

    Upload sample images: (Populates the database with sample data)
    upload-samples

    Set server ports for the client: (Updates the ports the client tries to connect to)
    ports <rest_port> <grpc_port>

    Exit the program:
    exit

Handling Spaces in Arguments
For command arguments that contain spaces (e.g., author names, image titles), enclose the value in double quotation marks ("). Tags should be comma-separated without spaces unless the tag itself contains a space (which is generally discouraged).

Example:
upload image.jpg "Great image" "Amazing Photographer" nature,landscape

Command Examples
Listing Images
    List all images:
    list

    List images by a specific author:
    list --author "Photographer 1"

    List images matching specific tags (comma-separated):
    list --tags landscape,nature

Uploading an Image

upload path/to/image.jpg "Campus fountain" "Seattle University" architecture,fountain,urban

Updating an Image

    Update title and author for image ID 3:
    update 3 --title "New Title" --author "New Author"

    Update only the tags for image ID 5:
    update 5 --tags nature,wildlife,animal

Exporting Images

    Export all images to a specific directory named my_exports:
    export --dir my_exports

    Export images by a specific author matching certain tags:
    export --author "John Photo" --tags landscape

Sample Images

To quickly populate the database with some sample data for testing, use the upload-samples command in the client:
upload-samples

