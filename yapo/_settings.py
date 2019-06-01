import os

_MONTHS_PER_YEAR = 12

data_url = os.environ.get('DATA_URL', 'https://okama.io/api/data-v0.1.3/')
change_column_name = 'close_pctchange'
