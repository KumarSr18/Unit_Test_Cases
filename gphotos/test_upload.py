import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from unittest.mock import patch, mock_open  # Import mock_open here
import json
from upload import parse_args, auth, get_authorized_session, save_cred, getAlbums, create_or_retrieve_album, upload_photos

class TestPhotoUploadScript(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_parse_args):
        mock_parse_args.return_value = MagicMock(auth_file='auth.json', album_name='Vacation', log_file='upload.log', photos=['photo1.jpg', 'photo2.jpg'])
        args = parse_args(['--auth', 'auth.json', '--album', 'Vacation', '--log', 'upload.log', 'photo1.jpg', 'photo2.jpg'])
        self.assertEqual(args.auth_file, 'auth.json')
        self.assertEqual(args.album_name, 'Vacation')
        self.assertEqual(args.log_file, 'upload.log')
        self.assertEqual(args.photos, ['photo1.jpg', 'photo2.jpg'])

    @patch('upload.InstalledAppFlow')
    def test_auth(self, mock_flow):
        mock_credentials = MagicMock()
        mock_credentials.credentials = 'dummy_credentials'
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_credentials
        scopes = ['dummy_scope']
        credentials = auth(scopes)
        self.assertEqual(credentials.credentials, 'dummy_credentials')

    @patch('upload.Credentials')
    @patch('os.path')
    @patch('upload.auth')
    @patch('upload.save_cred')
    def test_get_authorized_session(self, mock_auth, mock_os_path, mock_credentials,mock_save_cred):
        mock_os_path.isfile.return_value = True
        mock_credentials.from_authorized_user_file.return_value = MagicMock()
        mock_save_cred.return_value = None 
        session = get_authorized_session('dummy_auth_file')
        self.assertIsNotNone(session)

    @patch('builtins.open', unittest.mock.mock_open())
    def test_save_cred(self):
        cred = MagicMock(token='dummy_token', refresh_token='dummy_refresh_token', id_token='dummy_id_token', scopes=['dummy_scope'], token_uri='dummy_token_uri', client_id='dummy_client_id', client_secret='dummy_client_secret')
        save_cred(cred, 'dummy_auth_file')
        open.assert_called_with('dummy_auth_file', 'w')

    @patch('upload.AuthorizedSession')
    def test_getAlbums(self, mock_session):
        mock_session.return_value.get.return_value.json.return_value = {'albums': [{'id': '1', 'title': 'Vacation'}]}
        albums = list(getAlbums(mock_session(), False))
        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0]['title'], 'Vacation')

    @patch('upload.getAlbums')
    @patch('upload.AuthorizedSession')
    def test_create_or_retrieve_album(self, mock_session, mock_getAlbums):
        mock_getAlbums.return_value = iter([{'id': '1', 'title': 'Vacation'}])
        album_id = create_or_retrieve_album(mock_session(), 'Vacation')
        self.assertEqual(album_id, '1')

    # Add more tests for upload_photos and other functions as neede


    # @patch('upload.AuthorizedSession')
    # @patch('upload.open', new_callable=unittest.mock.mock_open(), read_data=b'dummy image data')
    # @patch('upload.logging')
    # def test_upload_photos_success(self, mock_logging, mock_open, mock_authorized_session):
    #     mock_session_instance = mock_authorized_session.return_value
    #     mock_session_post = mock_session_instance.post
    #     mock_session_post.side_effect = [
    #         MagicMock(status_code=200, content=b'mock_upload_token'),  # Simulate successful upload token retrieval
    #         MagicMock(status_code=200, json=lambda: {"newMediaItemResults": [{"status": {"code": 0}}]})  # Simulate successful photo addition
    #     ]

    #     try:
    #         upload_photos(session=mock_session_instance, photo_file_list=['dummy.jpg'], album_name='Test Album')
    #     except Exception as e:
    #         self.fail(f"upload_photos raised an exception: {e}")

    #     # Adjust the assertion to match the correct log message
    #     mock_logging.info.assert_called_with("Added 'dummy.jpg' to library and album 'Test Album'")



    @patch('upload.AuthorizedSession')
    @patch('upload.open', new_callable=unittest.mock.mock_open(), read_data=b'dummy image data')
    @patch('upload.logging')
    def test_upload_photos_failure(self, mock_logging, mock_open, mock_authorized_session):
        mock_session_instance = mock_authorized_session.return_value
        mock_session_post = mock_session_instance.post
        mock_session_post.side_effect = [
            MagicMock(status_code=200, content=b'mock_upload_token'),  # First call for upload token
            MagicMock(status_code=500, json=lambda: {"error": {"message": "Internal Server Error"}})  # Second call for batch create simulating a failure
        ]
        
        upload_photos(session=mock_session_instance, photo_file_list=['dummy.jpg'], album_name='Test Album')
        #mock_logging.info.assert_called_with("Could not upload 'dummy.jpg'. Server Response - <MagicMock name='AuthorizedSession().post()' id='1234'>")
        mock_logging.error.assert_any_call(mock.ANY)
    
        #found_calls = [call for call in mock_logging.info.call_args_list if "Could not upload 'dummy.jpg'." in call[0][0]]
        #assert found_calls, "Expected log message not found."


if __name__ == '__main__':
    unittest.main()


# python -m coverage run -m unittest discover
# python -m coverage report    

# Name             Stmts   Miss  Cover
# ------------------------------------
# test_upload.py      61      1    98%
# upload.py          110     47    57%
# ------------------------------------
# TOTAL              171     48    72%