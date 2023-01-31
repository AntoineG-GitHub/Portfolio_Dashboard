import os

from content import application


def main():
    from content import app
    import callbacks
    app.run_server(debug=False, host='0.0.0.0')  # , host='0.0.0.0'


if __name__ == "__main__":
    main()
