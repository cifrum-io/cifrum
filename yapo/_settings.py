import os

_MONTHS_PER_YEAR = 12

data_url = os.environ.get('DATA_URL', 'https://okama.io/api/data/')
print('DATA_URL: {}'.format(data_url))
change_column_name = 'close_pctchange'
