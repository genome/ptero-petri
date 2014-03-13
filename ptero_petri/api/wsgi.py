from ptero_petri.api import application

app = application.create_app()


if __name__ == '__main__':
    app.run()
