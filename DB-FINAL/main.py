from website import application
from website.views import views 

app = application()


if __name__ == '__main__':
    app.run(debug=True)