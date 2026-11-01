from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Module-level proxy, tách rời để tránh import vòng và cho phép khởi tạo nhiều app (Slide 13-14)
db = SQLAlchemy()
migrate = Migrate()

