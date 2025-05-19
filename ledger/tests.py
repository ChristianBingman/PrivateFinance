import pytest

def test_create_transaction():
    # A double and many entry transaction should create
    ...

def test_create_transaction_with_invalid_decimal():
    # Amounts that don't abide by the fraction traded should fail
    ...

def test_invalid_transaction_amount():
    # All transactions should equal 0 in double entry
    ...

def test_default_transaction_values():
    # Test the default values for transaction and transaction details
    ...

def test_account_deletion_restricted():
    # Deleting an account without also deleting the entries should be restricted
    ...

def test_account_transaction_query():
    # Test querying all transactions by account
    ...

def test_query_entries_by_transaction():
    # Test querying all entries related to transaction detail
    ...
