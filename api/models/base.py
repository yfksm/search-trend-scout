from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Nothing else needed here, we just need a shared Base to avoid circular imports.
