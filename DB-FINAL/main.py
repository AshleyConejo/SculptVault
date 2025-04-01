import sys
import os

# Add the current directory to the module search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from website import application
from website.views import views

app = application()

if __name__ == '__main__':
    app.run(debug=True)
