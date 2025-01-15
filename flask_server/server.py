from flask import Flask, jsonify, send_file, abort, after_this_request
import os
import logging

# Base directory of the application
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO)


class FileMetadata:
    """Represents the metadata of a file."""

    def __init__(
        self,
        uuid: str,
        create_datetime: str,
        size: int,
        mimetype: str,
        name: str,
        path: str,
    ) -> None:
        """
        Initialize file metadata.

        :param uuid: UUID of the file.
        :param create_datetime: Creation date and time of the file.
        :param size: Size of the file in bytes.
        :param mimetype: MIME type of the file.
        :param name: Name of the file.
        :param path: Path to the file on disk.
        """
        self.uuid: str = uuid
        self.create_datetime: str = create_datetime
        self.size: int = size
        self.mimetype: str = mimetype
        self.name: str = name
        self.path: str = path

    def to_dict(self) -> dict:
        """
        Return the metadata of the file as a dictionary.

        :return: Dictionary representation of file metadata.
        """
        return {
            "create_datetime": self.create_datetime,
            "size": self.size,
            "mimetype": self.mimetype,
            "name": self.name,
        }


class FileService:
    """Provides services for managing files."""

    def __init__(self, files_metadata: dict[str, FileMetadata] | None = None) -> None:
        """
        Initialize the file service with metadata.

        :param files_metadata: Dictionary of file metadata.
        """
        self.files_metadata: dict[str, FileMetadata] = files_metadata or {}

    def add_file_metadata(self, file_metadata: FileMetadata) -> None:
        """
        Add a new file's metadata.

        :param file_metadata: Metadata of the file to be added.
        """
        self.files_metadata[file_metadata.uuid] = file_metadata

    def delete_file_metadata(self, uuid: str) -> None:
        """
        Delete a file's metadata by its UUID.

        :param uuid: UUID of the file to be deleted.
        """
        self.files_metadata.pop(uuid, None)

    def get_file_metadata(self, uuid: str) -> FileMetadata | None:
        """
        Return the metadata of a file by its UUID.

        :param uuid: UUID of the file.
        :return: FileMetadata instance or None if not found.
        """
        return self.files_metadata.get(uuid)

    def file_exists(self, uuid: str) -> bool:
        """
        Check if the file exists by its UUID.

        :param uuid: UUID of the file.
        :return: True if the file exists, False otherwise.
        """
        file_data: FileMetadata | None = self.get_file_metadata(uuid)
        return file_data is not None and os.path.exists(file_data.path)


class FileAPI:
    """Handles API routes for file operations."""

    def __init__(self, app: Flask, file_service: FileService) -> None:
        """
        Initialize the FileAPI with a Flask app and file service.

        :param app: Flask application instance.
        :param file_service: FileService instance to manage files.
        """
        self.app = app
        self.file_service: FileService = file_service
        self.register_routes()

    def register_routes(self) -> None:
        """
        Register all API endpoints.
        """
        self.app.add_url_rule(
            "/file/<uuid>/stat/", view_func=self.file_stat, methods=["GET"]
        )
        self.app.add_url_rule(
            "/file/<uuid>/read/", view_func=self.read_file, methods=["GET"]
        )

    def file_stat(self, uuid: str):
        """
        Endpoint for retrieving the metadata of a file.

        :param uuid: UUID of the file.
        :return: JSON response with file metadata or 404 if not found.
        """
        file_data: FileMetadata | None = self.file_service.get_file_metadata(uuid)

        if file_data:
            return jsonify(file_data.to_dict())
        else:
            logging.error(f"File with UUID {uuid} not found.")
            abort(404, description=f"File with UUID {uuid} not found.")

    def read_file(self, uuid: str):
        """
        Endpoint for reading the content of a file.

        :param uuid: UUID of the file.
        :return: File response for download or 404 if not found.
        """
        file_data: FileMetadata | None = self.file_service.get_file_metadata(uuid)

        if file_data:
            if not os.path.exists(file_data.path):
                logging.error(f"File with UUID {uuid} not found on disk.")
                abort(404, description=f"File with UUID {uuid} not found.")

            @after_this_request
            def close_file(response):
                """
                Close the file stream after the request is complete.

                :param response: Response object.
                :return: Modified response object.
                """
                try:
                    response.direct_passthrough = False
                    response.stream.close()
                except Exception as e:
                    logging.exception("Error closing file stream.")
                return response

            return send_file(
                file_data.path,
                mimetype=file_data.mimetype,
                as_attachment=True,
                download_name=file_data.name,
            )
        else:
            logging.error(f"File with UUID {uuid} not found.")
            abort(404, description=f"File with UUID {uuid} not found.")


# Initialize Flask app
app = Flask(__name__)

# Predefined metadata for testing
initial_metadata: dict[str, FileMetadata] = {
    "1234": FileMetadata(
        uuid="1234",
        create_datetime="2023-09-20T12:34:56Z",
        size=12345,
        mimetype="text/plain",
        name="example.txt",
        path=os.path.join(BASE_DIR, "example.txt"),
    )
}

file_service = FileService(files_metadata=initial_metadata)
file_api = FileAPI(app, file_service)

if __name__ == "__main__":
    app.run(debug=True)
