# data_gathering.py
import re
import os
import csv
import unittest
import requests
import matplotlib.pyplot as plt
import sqlite3
import json
# To account for inconsistent date formatting
from datetime import datetime
import my_keys


# API Keys
google_books_key = my_keys.GOOGLE_BOOKS_KEY
# No Open Library API Key needed!

# GLOBAL CONSTANTS
GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_BASE_URL = "https://openlibrary.org/search.json"
DATABASE_NAME = "book_trends.db"
GOOGLE_BOOKS_RECORDS_TO_GATHER = 100
OPEN_LIBRARY_RECORDS_TO_GATHER = 100
API_CALL_LIMIT = 25
USER_AGENT = 'BookTrendAnalyzer (jbachrach36@gmail.com)'



# CREATE DATABASE
def set_up_database(db_name):
    """
    Sets up a connection to an SQLite database.
    Creates full path to the database file.
    Creates the database file if it doesn't exist.
    Creates a cursor object to execute SQL commands.

    Args:
        db_name (str): The name of the database file.

    Returns:
        tuple: A tuple containing the cursor and connection objects.
    """

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(os.path.join(path, db_name))
    cur = conn.cursor()
    return cur, conn


# CREATE TABLES
def create_tables(cur, conn):
    """
    Use SQL to create the 'Books' and 'Topic_Trends' tables

    Args:
        cur: the cursor object
        conn: the connection object
    """
    #Create Books table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            author TEXT,
            publication_date TEXT NOT NULL,
            source_api TEXT NOT NULL,
            subject_categories TEXT
        )
    ''')

    # Create Topic_Trends table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Topic_Trends (
            trend_id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            topic TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            book_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES Books(book_id)
        )
    ''')
    conn.commit()
    



# GET GOOGLE BOOKS JSON
def get_google_books_json(query, max_results=API_CALL_LIMIT, start_index=0):
    pass



# GET OPEN LIBRARY JSON
def get_openlibrary_json(query, limit=API_CALL_LIMIT, page=1):
    pass



# PROCESS GOOGLE BOOKS DATA
def process_google_books_data(cur, conn, data, target_genres):
    pass



# PROCESS OPEN LIBRARY DATA
def process_open_library_data(cur, conn, data, target_genres):
    pass



# GATHER GOOGLE BOOKS DATA
def gather_google_books_data(cur, conn, query, num_records, target_genres):
    pass



# GATHER OPEN LIBRARY DATA
def gather_open_library_data(cur, conn, query, num_records, target_genres):
    pass
