"""Small runner to create and inspect DB tables for manual testing."""
from .logic import DatabaseManager


def main():
    dm = DatabaseManager()
    dm.create_tables()
    print("Tables in database:")
    for t in dm.list_tables():
        print(" -", t)


if __name__ == "__main__":
    main()
