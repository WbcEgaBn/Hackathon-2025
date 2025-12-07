# scripts/init_db.py

from db.database import Base, engine
from db import models

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
