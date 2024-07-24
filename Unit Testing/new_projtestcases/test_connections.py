import unittest
from unittest.mock import patch, MagicMock
from connections import get_data, format_data, load 
import uuid

class TestAPIFunctions(unittest.TestCase):

    @patch('requests.get')
    def test_get_data(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{
                "name": {"first": "John", "last": "Doe"},
                
            }]
        }
        mock_get.return_value = mock_response

        # Call the function
        data = get_data()

        # Assertions
        self.assertEqual(data['name']['first'], "John")
        self.assertEqual(data['name']['last'], "Doe")
        
    def test_format_data(self):
        # Sample response that mimics the API response
        sample_response = {
            "name": {"first": "John", "last": "Doe"},
            "location": {
                "street": {"number": 123, "name": "Main St"},
                "city": "Sample City",
                "state": "Sample State",
                "country": "Sample Country",
                "postcode": "12345"
            },
            "gender": "male",
            "email": "john.doe@example.com",
            "login": {"username": "johndoe123"},
            "dob": {"date": "1990-01-01T00:00:00Z"},
            "registered": {"date": "2010-09-24T00:00:00Z"},
            "phone": "123-456-7890",
            "picture": {"medium": "http://example.com/johndoe.jpg"}
        }

        # Call the function
        formatted_data = format_data(sample_response)

        # Assertions
        self.assertIsInstance(formatted_data['id'], uuid.UUID)
        self.assertEqual(formatted_data['first_name'], "John")
        self.assertEqual(formatted_data['last_name'], "Doe")
        self.assertEqual(formatted_data['gender'], sample_response['gender'])
        expected_address = "123 Main St, Sample City, Sample State, Sample Country"
        self.assertEqual(formatted_data['address'], expected_address)
        self.assertEqual(formatted_data['post_code'], sample_response['location']['postcode'])
        self.assertEqual(formatted_data['email'], sample_response['email'])
        self.assertEqual(formatted_data['username'], sample_response['login']['username'])
        self.assertEqual(formatted_data['dob'], sample_response['dob']['date'])
        self.assertEqual(formatted_data['registered_date'], sample_response['registered']['date'])
        self.assertEqual(formatted_data['phone'], sample_response['phone'])
        self.assertEqual(formatted_data['picture'], sample_response['picture']['medium'])


    def test_load(self):
    # Mock data to be loaded
        mock_data = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "male",
            "address": "123 Main St, Sample City, Sample State, Sample Country",
            "post_code": "12345",
            "email": "john.doe@example.com",
            "username": "johndoe123",
            "dob": "1990-01-01T00:00:00Z",
            "registered_date": "2010-09-24T00:00:00Z",
            "phone": "123-456-7890",
            "picture": "http://example.com/john.jpg"
        }

    # Expected SQL command
        expected_sql = """
            INSERT INTO RandomData (id, first_name, last_name, gender, address, post_code, email, username, dob, registered_date, phone, picture)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    # Mock the pd.DataFrame.to_csv method to do nothing
        with unittest.mock.patch('pandas.DataFrame.to_csv') as mock_to_csv:
            # Mock the pyodbc.connect method to return a mock connection object
            with unittest.mock.patch('pyodbc.connect') as mock_connect:
                mock_conn = mock_connect.return_value
                mock_cursor = mock_conn.cursor.return_value

                # Call the function under test
                load(mock_data)

                # Assert that to_csv was called once
                mock_to_csv.assert_called_once()

                # Assert that connect was called with the correct connection string
                mock_connect.assert_called_once_with("Driver={SQL Server};Server=LAPTOP-CU043492\SQLEXPRESS;Database=master;Uid=KumarSr;Pwd=Srijivas@123;")

                # Assert that the cursor executed the expected SQL command with the correct parameters
                mock_cursor.execute.assert_called_once_with(expected_sql, 1, "John", "Doe", "male", "123 Main St, Sample City, Sample State, Sample Country", "12345", "john.doe@example.com", "johndoe123", "1990-01-01T00:00:00Z", "2010-09-24T00:00:00Z", "123-456-7890", "http://example.com/john.jpg")

                # Assert that the connection was committed and both cursor and connection were closed
                mock_conn.commit.assert_called_once()
                mock_cursor.close.assert_called_once()
                mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()