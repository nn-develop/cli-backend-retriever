import os

# Default values for backend
DEFAULT_GRPC_SERVER: str = os.getenv("GRPC_SERVER", "localhost:50051")
DEFAULT_REST_URL: str = os.getenv("REST_URL", "http://localhost:5000")

# Default output (stdout)
DEFAULT_OUTPUT: str = "-"

# Backend possible choices
BACKEND_GRPC: str = "grpc"
BACKEND_REST: str = "rest"
DEFAULT_SERVER_TYPE: str = BACKEND_REST
