"""
SQLite database manager for X-Cleaner.

This module handles all database operations including schema initialization,
account storage, and data retrieval.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import CategorizedAccount


class DatabaseManager:
    """
    SQLite database manager for account storage.

    Manages the local SQLite database for storing categorized accounts
    and category metadata.
    """

    def __init__(self, db_path: str = "data/accounts.db"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory_exists()
        self._init_db()

    def _ensure_data_directory_exists(self) -> None:
        """Create data directory if it doesn't exist."""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                display_name TEXT,
                bio TEXT,
                verified INTEGER,
                created_at TEXT,
                followers_count INTEGER,
                following_count INTEGER,
                tweet_count INTEGER,
                location TEXT,
                website TEXT,
                profile_image_url TEXT,
                category TEXT,
                confidence REAL,
                reasoning TEXT,
                analyzed_at TEXT,
                updated_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                characteristics TEXT,
                estimated_percentage REAL,
                account_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_category
            ON accounts(category)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_verified
            ON accounts(verified)
        """)

        conn.commit()
        conn.close()

    def save_accounts(self, accounts: List[CategorizedAccount]) -> None:
        """
        Save or update accounts.

        Args:
            accounts: List of categorized accounts to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for account in accounts:
            cursor.execute(
                """
                INSERT OR REPLACE INTO accounts VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """,
                (
                    account.user_id,
                    account.username,
                    account.display_name,
                    account.bio,
                    int(account.verified),
                    account.created_at.isoformat() if account.created_at else None,
                    account.followers_count,
                    account.following_count,
                    account.tweet_count,
                    account.location,
                    account.website,
                    account.profile_image_url,
                    account.category,
                    account.confidence,
                    account.reasoning,
                    account.analyzed_at.isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

    def get_all_accounts(self) -> List[CategorizedAccount]:
        """
        Retrieve all accounts.

        Returns:
            List of all categorized accounts in database
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accounts")
        rows = cursor.fetchall()

        accounts = [self._row_to_account(row) for row in rows]

        conn.close()
        return accounts

    def get_accounts_by_category(self, category: str) -> List[CategorizedAccount]:
        """
        Get all accounts in a specific category.

        Args:
            category: Category name

        Returns:
            List of accounts in the specified category
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accounts WHERE category = ?", (category,))
        rows = cursor.fetchall()

        accounts = [self._row_to_account(row) for row in rows]

        conn.close()
        return accounts

    def get_categories(self) -> List[dict]:
        """
        Get all categories with metadata.

        Returns:
            List of category dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM categories")
        rows = cursor.fetchall()

        categories = [dict(row) for row in rows]

        conn.close()
        return categories

    def save_categories(self, categories_data: dict) -> None:
        """
        Save discovered categories metadata.

        Args:
            categories_data: Dictionary containing categories information
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for category in categories_data.get("categories", []):
            cursor.execute(
                """
                INSERT OR REPLACE INTO categories
                (name, description, characteristics, estimated_percentage, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    category["name"],
                    category.get("description", ""),
                    str(category.get("characteristics", [])),
                    category.get("estimated_percentage", 0),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

    def _row_to_account(self, row: sqlite3.Row) -> CategorizedAccount:
        """
        Convert database row to CategorizedAccount.

        Args:
            row: SQLite row object

        Returns:
            CategorizedAccount instance
        """
        return CategorizedAccount(
            user_id=row["user_id"],
            username=row["username"],
            display_name=row["display_name"],
            bio=row["bio"],
            verified=bool(row["verified"]),
            created_at=datetime.fromisoformat(row["created_at"])
            if row["created_at"]
            else None,
            followers_count=row["followers_count"],
            following_count=row["following_count"],
            tweet_count=row["tweet_count"],
            location=row["location"],
            website=row["website"],
            profile_image_url=row["profile_image_url"],
            category=row["category"],
            confidence=row["confidence"],
            reasoning=row["reasoning"],
            analyzed_at=datetime.fromisoformat(row["analyzed_at"]),
        )
