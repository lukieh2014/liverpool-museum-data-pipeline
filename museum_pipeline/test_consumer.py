# pylint: skip-file

import pytest
from unittest.mock import patch, MagicMock
from consumer import convert_to_date_frac, validate_msg


@patch('consumer.log_error')
def test_invalid_date1(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:40:23.587096", "site": "3", "val": "3"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_invalid_date2(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 18:20:23.587096", "site": "3", "val": "3"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_valid_date(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "3", "val": "3"}, 'test', 'test') == {"cont": True, "at": "2024-10-23 08:46:23.587096", "site": 3, "val": 3, "type": 99}


def test_converting_date_to_frac():
    assert convert_to_date_frac('2024-10-23 09:15:00.000000') == 9.25
    assert convert_to_date_frac('2024-10-23 09:45:00.000000') == 9.75


@patch('consumer.log_error')
def test_invalid_site_type(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "A", "val": "3"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_invalid_val_type(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "3", "val": "NA"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_invalid_site_value(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "6", "val": "3"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_invalid_val_value(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "3", "val": "5"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_invalid_type_value(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "3", "val": "-1", "type": "2"}, 'test', 'test') == {"cont": False}


@patch('consumer.log_error')
def test_valid_emergency(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "3", "val": "-1", "type": "1"}, 'test', 'test') == {"cont": True, "at": "2024-10-23 08:46:23.587096", "site": 3, "val": -1, "type": 1}


@patch('consumer.log_error')
def test_missing_keys(patch_log_error):
    patch_log_error.return_value = None

    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "site": "3", "val": "-1"}, 'test', 'test') == {"cont": False}
    assert validate_msg(
        {"at": "2024-10-23 08:46:23.587096", "val": "4"}, 'test', 'test') == {"cont": False}
