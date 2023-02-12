import os

from pages.content import application


def main():
    from pages.content import app
    import utils.callbacks as callbacks
    app.run_server(debug=False, host='0.0.0.0')  # , host='0.0.0.0'


if __name__ == "__main__":
    main()
