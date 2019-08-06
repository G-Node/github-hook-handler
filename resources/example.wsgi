import sys
sys.path.insert(0, '/path/to/application/github-hook-handler/')

from handlers import example

listener = example.create_app('secret_token_value')
application = listener.app
