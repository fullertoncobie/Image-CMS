Assignment 2

Prerequisites
A requirements.txt file is included. Run the file with:
	pip install -r requirements.txt

Server Setup
To setup the server, run main.py, which will create the database, establish servers for REST and gRPC apis, and initialize the relevant infrastructure.

main.py has two option arguments for specifying the port for either server. Default values will be used if these are not provided.
	python main.py [--rest-port PORT] [--grpc-port PORT]

Client Usage
A sample client in the form of a CLI has been provided. The sample client will default to the default ports of the servers unless otherwise specific in optional arguments.
	python client.py [--rest-port PORT] [--grpc-port PORT]
The CLI has the following commands:
- List all images with optional filters
	list [--author "<author>"] [--tags <tags>]  
- Get image by ID  
	get <id>
- Upload an image (use quotes for values with spaces)                              
	upload <file> "<title>" "<author>" <tags>   
- Update an image
	update <id> [--title "<title>"] [--author "<author>"] [--tags <tags>] 
- Delete an image
	delete <id>                                 
- Export images to files
	export [--author "<author>"] [--tags <tags>] [--dir <directory>] 
- Upload sample images
	upload-samples
- Set server ports
	ports <rest> <grpc>                         
- Exit the program
	exit 
                                       
Spaces In Arguments
For values that contain spaces (like author names or image titles), use quotation marks around the value:
upload image.jpg "Great image" "Amazing Photographer" nature,landscape

Listing images
list
list --author "Photographer 1"
list --tags landscape,nature

Uploading an image
upload path/to/image.jpg "Campus fountain" "Seattle University" architecture,fountain,urban

Updating an image
update 3 --title "New Title" --author "New Author"
update 5 --tags nature,wildlife,animal

Exporting Images
export --dir my_exports
export --author "John Photo" --tags landscape

Sample Images
The client includes a feature to upload sample images to populate the database by running:
Upload-samples