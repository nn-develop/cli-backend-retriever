import requests


class RestClient:
    """
    Client for interacting with a REST API to manage files.
    """

    def __init__(self, base_url: str):
        """
        Initialize RestClient with base URL.

        :param base_url: Base URL for the REST API.
        """
        self.base_url: str = base_url

    def get_file_stat(self, uuid: str) -> dict:
        """
        Get file metadata by UUID.

        :param uuid: UUID of the file.
        """
        url: str = f"{self.base_url}/file/{uuid}/stat/"
        response: requests.Response = requests.get(url)
        match response.status_code:
            case 200:
                return response.json()
            case 404:
                raise FileNotFoundError(f"File with UUID {uuid} not found.")
            case _:
                raise Exception(
                    f"Failed with file with UUID {uuid}. Status code: {response.status_code}"
                )

    def read_file(self, uuid: str) -> tuple[str, bytes]:
        """
        Read file content by UUID.

        :param uuid: UUID of the file.
        """
        url: str = f"{self.base_url}/file/{uuid}/read/"
        response: requests.Response = requests.get(url)
        match response.status_code:
            case 200:
                disposition: str = response.headers.get("Content-Disposition", "")
                if "filename=" in disposition:
                    file_name: str = disposition.split("filename=")[-1].strip('"')
                else:
                    file_name = "unknown_filename"
                file_content: bytes = response.content
                return file_name, file_content

            case 404:
                raise FileNotFoundError(f"File with UUID {uuid} not found.")
            case _:
                raise Exception(
                    f"Failed to read file with UUID {uuid}. Status code: {response.status_code}"
                )
