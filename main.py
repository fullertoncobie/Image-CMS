import threading
import uvicorn
import logging
import grpc
import argparse
from api import grpc_server

from db import database

grpc_server_instance = grpc_server.create_grpc_server()

def run_rest_server(port):
    """Start the REST API server"""
    print(f"Starting REST server on port {port}...")
    uvicorn.run("api.rest_api:app", host="0.0.0.0", port=port, log_level="info")

def run_grpc_server(port):
    """Start the gRPC server"""
    print(f"Starting gRPC server on port {port}...")
    grpc_server_instance.add_insecure_port(f'[::]:{port}')
    grpc_server_instance.start()
    grpc_server_instance.wait_for_termination()

# Main program
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start the REST and gRPC servers')
    parser.add_argument('--rest-port', type=int, default=8001,
                        help='Port for the REST API server (default: 8001)')
    parser.add_argument('--grpc-port', type=int, default=50051,
                        help='Port for the gRPC server (default: 50051)')
    args = parser.parse_args()
    
    # Initialize database
    database.init_db()

    # Start both servers in separate threads
    rest_thread = threading.Thread(target=run_rest_server, args=(args.rest_port,))
    grpc_thread = threading.Thread(target=run_grpc_server, args=(args.grpc_port,))
    
    rest_thread.start()
    grpc_thread.start()
    
    # Wait for the threads to complete
    rest_thread.join()
    grpc_thread.join()

    print("Application stopped")