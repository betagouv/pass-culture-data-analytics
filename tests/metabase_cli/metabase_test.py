from metabase_cli.metabase import configure_new_metabase_session, get_dump_table_id, get_dump_table_information, \
     get_db_details_by_app_name, get_app_name_for_restore, edit_dump_table_connection
from unittest.mock import patch, MagicMock
import json


ENV_VAR = {
    "METABASE_USER_NAME": "admin.metabase@example.com",
    "METABASE_PASSWORD": "password",
    "METABASE_DBNAME": "table_name",
    "BLUE_DB_INFO": """{
        "app_name": "app_name_blue",
        "details": {
            "port": "12345",
            "host": "db_blue.postgresql.example.com",
            "dbname": "db_blue",
            "user": "db_user",
            "password": "password_blue"
        }
    }""",
    "GREEN_DB_INFO": """{
        "app_name": "app_name_green",
        "details": {
            "port": "12346",
            "host": "db_green.postgresql.example.com",
            "dbname": "db_green",
            "user": "db_user",
            "password": "password_green"
        }
    }"""
}

@patch('metabase_cli.metabase.METABASE_URL', 'metabase.example.com')
@patch('metabase_cli.metabase.requests.post')
def test_configure_new_metabase_session(mock_request):
    # Given
    user_name = 'admin.metabase@example.com'
    password = 'password'
    request_json = {"id": "session_id"}
    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(return_value=request_json)
    mock_request.return_value = response_return_value

    # When
    result = configure_new_metabase_session(user_name, password)

    # Then
    assert result == 'session_id'
    mock_request.assert_called_once_with('metabase.example.com/api/session/',
     json={'username': 'admin.metabase@example.com',
    'password': 'password'})


@patch('metabase_cli.metabase.METABASE_URL', 'metabase.example.com')
@patch('metabase_cli.metabase.requests.get')
def test_get_dump_table_id(mock_request):
    # Given
    session_id = 42
    request_json = [{'name': 'table_name', 'id': 'table_id_in_metabase'}]
    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(return_value=request_json)
    mock_request.return_value = response_return_value

    # When
    result = get_dump_table_id('table_name', session_id)

    # Then
    assert result == 'table_id_in_metabase'
    mock_request.assert_called_once_with('metabase.example.com/api/database/',
     headers={'cookie': 'metabase.SESSION=42'})


@patch('metabase_cli.metabase.METABASE_URL', 'metabase.example.com')
@patch('metabase_cli.metabase.get_dump_table_id')
@patch('metabase_cli.metabase.requests.get')
def test_get_dump_table_information(mock_request, mock_get_dump_table_id):
    # Given
    session_id = 42
    request_json = {
        'name': 'table_name',
        'id': 'table_id_in_metabase',
        'details': {'port': '12345',
                    'host': 'db_name.postgresql.example.com',
                    'dbname': 'db_name',
                    'user': 'db_user',
                    'password': 'password',
                    'ssl': True},
    }
    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(return_value=request_json)
    mock_request.return_value = response_return_value
    mock_get_dump_table_id.return_value = 'table_id_in_metabase'

    # When
    result = get_dump_table_information('table_name', session_id)

    # Then
    assert result == 'db_name.postgresql.example.com'
    mock_request.assert_called_once_with('metabase.example.com/api/database/table_id_in_metabase',
     headers={'cookie': 'metabase.SESSION=42'})


@patch.dict('os.environ', ENV_VAR)
def test_get_db_details_by_app_name_return_blue_db_details_when_app_name_match():
    # Given / When
    result = get_db_details_by_app_name('app_name_blue')

    # Then
    assert result == {
        "port": "12345",
        "host": "db_blue.postgresql.example.com",
        "dbname": "db_blue",
        "user": "db_user",
        "password": "password_blue"
    }


@patch.dict('os.environ', ENV_VAR)
def test_get_db_details_by_app_name_return_green_db_details_when_app_name_does_not_match():
    # Given / When
    result = get_db_details_by_app_name('other_app_name')

    # Then
    assert result == {
        "port": "12346",
        "host": "db_green.postgresql.example.com",
        "dbname": "db_green",
        "user": "db_user",
        "password": "password_green"
    }


@patch.dict('os.environ', ENV_VAR)
@patch('metabase_cli.metabase.get_dump_table_information')
@patch('metabase_cli.metabase.configure_new_metabase_session')
def test_get_app_name_for_restore_return_green_app_name_when_blue_db_is_on_metabase(mock_configure_new_metabase_session, mock_get_dump_table_information):
    # Given
    mock_configure_new_metabase_session.return_value = 'session_id'
    mock_get_dump_table_information.return_value = 'db_blue.postgresql.example.com'

    # When
    result = get_app_name_for_restore()

    # Then
    assert result == 'app_name_green'


@patch.dict('os.environ', ENV_VAR)
@patch('metabase_cli.metabase.get_dump_table_information')
@patch('metabase_cli.metabase.configure_new_metabase_session')
def test_get_app_name_for_restore_return_blue_app_name_when_green_db_is_on_metabase(mock_configure_new_metabase_session, mock_get_dump_table_information):
    # Given
    mock_configure_new_metabase_session.return_value = 'session_id'
    mock_get_dump_table_information.return_value = 'db_green.postgresql.example.com'

    # When
    result = get_app_name_for_restore()

    # Then
    assert result == 'app_name_blue'


@patch.dict('os.environ', ENV_VAR)
@patch('metabase_cli.metabase.METABASE_URL', 'metabase.example.com')
@patch('metabase_cli.metabase.requests.put')
@patch('metabase_cli.metabase.get_db_details_by_app_name')
@patch('metabase_cli.metabase.get_app_name_for_restore')
@patch('metabase_cli.metabase.get_dump_table_id')
@patch('metabase_cli.metabase.configure_new_metabase_session')
def test_edit_dump_table_connection(mock_configure_new_metabase_session, mock_get_dump_table_id, mock_get_app_name_for_restore, mock_get_db_details_by_app_name, mock_request):
    # Given
    table_name = 'table_name'
    user_name = 'user_name'
    password = 'password'
    mock_configure_new_metabase_session.return_value = 'session_id'
    mock_get_dump_table_id.return_value = 'table_id'
    mock_get_app_name_for_restore.return_value = 'app_name_blue'
    mock_get_db_details_by_app_name.return_value = {
        "port": "12345",
        "host": "db_blue.postgresql.example.com",
        "dbname": "db_blue",
        "user": "db_user",
        "password": "password_blue"
    }

    # When
    edit_dump_table_connection(table_name, user_name, password)

    # Then
    mock_request.assert_called_once_with('metabase.example.com/api/database/table_id',
     headers={'cookie': 'metabase.SESSION=session_id'},
     json={'details': {'port': '12345',
     'host': 'db_blue.postgresql.example.com',
     'dbname': 'db_blue',
     'user': 'db_user',
     'password': 'password_blue',
     'ssl': True},
     'name': 'table_name', 'engine': 'postgres'})

