from app.db.dbengine import engine
from app.models.models import Base

print("Creating table....")
Base.metadata.create_all(engine)
print("Table created successfully")