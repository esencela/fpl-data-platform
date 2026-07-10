import os

os.environ.setdefault('RAW_DATA_DIR', '/tmp/raw_data_test')

os.environ.setdefault('POSTGRES_DB', 'fpl_test')
os.environ.setdefault('POSTGRES_USER', 'test_user')
os.environ.setdefault('POSTGRES_PASSWORD', 'test_password')
os.environ.setdefault('POSTGRES_HOST', 'localhost')