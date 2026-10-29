""" Interactions with the database"""
import os
from sqlalchemy import create_engine, desc, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'word_path.db')}"

# Create database connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Generates sessions for routes
def get_db():
    with SessionLocal() as db:
        yield db


# ------ User Vocabulary ------
def get_user_vocabulary(db: Session, user_id: int):
    """Gets a specific users' vocabulary."""
    import data_models as dm

    return db.scalars(
        select(dm.UserSymbol)
        .where(dm.UserSymbol.user_id == user_id)
        .order_by(
            dm.UserSymbol.page,
            dm.UserSymbol.position,
            dm.UserSymbol.symbol_id,
        )
    ).all()


def update_user_vocabulary(
    db: Session,
    user_id: int,
    symbol_id: int,
    page: str,
):
    """Adds a symbol to the user's vocabulary."""
    import data_models as dm

    # Find last position on selected page
    last_symbol = db.scalars(
        select(dm.UserSymbol)
        .where(dm.UserSymbol.user_id == user_id)
        .where(dm.UserSymbol.page == page)
        .order_by(desc(dm.UserSymbol.position))
    ).first()

    if last_symbol is None:
        position = 1
    else:
        position = last_symbol.position + 1

    added_symbol = dm.UserSymbol(
        user_id=user_id, symbol_id=symbol_id, page=page, position=position
    )
    db.add(added_symbol)
    db.commit()
    db.refresh(added_symbol)

    return added_symbol
