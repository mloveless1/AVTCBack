from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

db = SQLAlchemy()


@contextmanager
def managed_transaction():
    """Context manager to manage a SQLAlchemy session for a web request lifecycle."""
    # Make sure to use the Flask app's current configuration
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        app.logger.error(f"Transaction failed and was rolled back: {e}")
        raise
    finally:
        session.close()
