from io import StringIO
import unittest
from unittest.mock import patch, mock_open, Mock
from file_client import FileClient


class TestFileClient(unittest.TestCase):

    def setUp(self) -> None:
        self.client: FileClient = FileClient(backend="rest", output="output.txt")

    @patch("builtins.open", new_callable=mock_open)
    def test_stat_write_output_to_file(self, mock_file: Mock) -> None:
        """Test if stat method correctly writes metadata to a file."""
        stat_data: dict = {
            "name": "example.txt",
            "size": 12345,
            "create_datetime": "2023-09-20T12:34:56Z",
            "mimetype": "text/plain",
        }

        with patch.object(self.client, "client") as mock_client:
            mock_client.get_file_stat.return_value = stat_data

            self.client.stat("some-uuid")

            expected_output: bytes = (
                "Name: example.txt\n"
                "Size: 12345 bytes\n"
                "Created: 2023-09-20T12:34:56Z\n"
                "MIME Type: text/plain\n"
            ).encode("utf-8")

            mock_file.assert_called_once_with("output.txt", "wb")
            mock_file().write.assert_called_once_with(expected_output)

    @patch("builtins.open", new_callable=mock_open)
    def test_stat_write_output_to_stdout(self, mock_file: Mock) -> None:
        """Test if stat method correctly writes metadata to stdout when output is '-'."""
        self.client.output = "-"
        stat_data: dict = {
            "name": "example.txt",
            "size": 12345,
            "create_datetime": "2023-09-20T12:34:56Z",
            "mimetype": "text/plain",
        }

        with patch.object(self.client, "client") as mock_client:
            mock_client.get_file_stat.return_value = stat_data

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                self.client.stat("some-uuid")

                expected_output = (
                    "Name: example.txt\n"
                    "Size: 12345 bytes\n"
                    "Created: 2023-09-20T12:34:56Z\n"
                    "MIME Type: text/plain\n"
                )
                self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch("builtins.open", new_callable=mock_open)
    def test_write_output_to_file(self, mock_file: Mock) -> None:
        """Test if write_output correctly writes content to a file."""
        file_name: str = "output.txt"
        file_content: bytes = b"File content here."

        self.client._write_output(file_content, file_name)

        mock_file.assert_called_once_with("output.txt", "wb")
        mock_file().write.assert_called_once_with(file_content)

    @patch("builtins.open", new_callable=mock_open)
    def test_write_output_to_stdout(self, mock_file: Mock) -> None:
        """Test if write_output correctly writes content to stdout."""
        self.client.output = "-"
        file_name: str = "example.txt"
        file_content: bytes = b"File content here."

        self.client._write_output(file_content, file_name)
        mock_file.assert_not_called()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.client._write_output(file_content, file_name)
            expected_output: str = file_content.decode("utf-8", errors="replace")
            self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == "__main__":
    unittest.main()
