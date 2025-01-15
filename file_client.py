#!/usr/bin/env python3
import sys
import argparse
from rest_client import RestClient
from grpc_client import GrpcClient

# from grpc_client import GrpcClient
from config import (
    BACKEND_REST,
    BACKEND_GRPC,
    DEFAULT_REST_URL,
    DEFAULT_GRPC_SERVER,
    DEFAULT_SERVER_TYPE,
    DEFAULT_OUTPUT,
)


class FileClient:
    """
    Client for interacting with file backend (REST or gRPC).
    """

    def __init__(
        self,
        backend: str,
        rest_base_url: str | None = None,
        grpc_server: str | None = None,
        output: str | None = None,
    ) -> None:
        """
        Initialize the FileClient with the given backend.

        :param backend: Type of backend (REST or gRPC).
        :param rest_base_url: Base URL for the REST server.
        :param grpc_server: Address of the gRPC server.
        :param output: Output file path or '-' for stdout.
        """
        self.output: str = output or DEFAULT_OUTPUT

        backend_clients = {
            BACKEND_REST: lambda: RestClient(rest_base_url or DEFAULT_REST_URL),
            BACKEND_GRPC: lambda: GrpcClient(grpc_server or DEFAULT_GRPC_SERVER),
        }

        try:
            self.client: RestClient | GrpcClient = backend_clients[backend]()
        except KeyError:
            raise ValueError(f"Unknown backend: {backend}")

    def stat(self, uuid: str) -> None:
        """
        Retrieve and output metadata of the file identified by UUID.

        :param uuid: UUID of the file.
        """
        stat_data: dict = self.client.get_file_stat(uuid)
        stat_output: str = self._format_stat(stat_data)
        self._write_output(stat_output.encode("utf-8"), f"{uuid}_stat.txt")

    def read(self, uuid: str) -> None:
        """
        Read and output the content of the file identified by UUID.

        :param uuid: UUID of the file.
        """
        file_name: str
        file_content: bytes
        result: tuple[str, bytes] | None = self.client.read_file(uuid)
        if result is None:
            raise ValueError(f"No file found with UUID: {uuid}")
        file_name, file_content = result
        self._write_output(file_content, file_name)

    def _format_stat(self, stat_data: dict) -> str:
        # from grpc_client import GrpcClient
        """
        Format file metadata into a string.

        :param stat_data: Metadata dictionary of the file.
        :return: Formatted metadata as a string.
        """
        return (
            f"Name: {stat_data['name']}\n"
            f"Size: {stat_data['size']} bytes\n"
            f"Created: {stat_data['create_datetime']}\n"
            f"MIME Type: {stat_data['mimetype']}\n"
        )

    def _write_output(self, content: bytes, file_name: str) -> None:
        """
        Write file content to the output destination.

        :param content: Content of the file.
        :param file_name: Name of the file.
        """
        if self.output == "-":
            sys.stdout.write(content.decode("utf-8", errors="replace"))
        else:
            with open(self.output, "wb") as f:
                f.write(content)


def main() -> None:
    """
    Parse command line arguments and execute the appropriate client command.
    """
    parser = argparse.ArgumentParser(
        description="CLI client to interact with REST or gRPC server.\n"
        "Usage: file-client [options] stat UUID\n"
        "       file-client [options] read UUID\n"
        "       file-client --help",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=["stat", "read"],
        help="Command to execute:\n"
        "stat - Prints the file metadata in a human-readable manner.\n"
        "read - Outputs the file content.",
    )
    parser.add_argument("uuid", help="UUID of the file")
    parser.add_argument(
        "--backend",
        choices=[BACKEND_GRPC, BACKEND_REST],
        default=DEFAULT_SERVER_TYPE,
        help=f"Backend to use (default: {DEFAULT_SERVER_TYPE})",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_REST_URL,
        help=f"Base URL for REST server (default: {DEFAULT_REST_URL})",
    )
    parser.add_argument(
        "--grpc-server",
        default=DEFAULT_GRPC_SERVER,
        help=f"Host and port of the gRPC server (default: {DEFAULT_GRPC_SERVER})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Set the output file (default: {DEFAULT_OUTPUT})",
    )

    args: argparse.Namespace = parser.parse_args()

    client: FileClient = FileClient(
        backend=args.backend,
        rest_base_url=args.base_url,
        grpc_server=args.grpc_server,
        output=args.output,
    )

    if args.command == "stat":
        client.stat(args.uuid)
    elif args.command == "read":
        client.read(args.uuid)


if __name__ == "__main__":
    main()
