from emailapp.helpers.sqlhelper import create_table
from emailapp import app
from conf.config import APP_HOST, APP_PORT, APP_DEBUG

if __name__ == "__main__":
    # create_table()
    app.run(host=APP_HOST, port=APP_PORT, debug=APP_DEBUG)
