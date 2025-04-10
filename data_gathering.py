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


#***Debug Print-statements are commented out

# API KEYS
google_books_key = my_keys.GOOGLE_BOOKS_KEY


# GLOBAL CONSTANTS
GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_BASE_URL = "https://openlibrary.org/search.json"
DATABASE_NAME = "book_trends.db"
GOOGLE_BOOKS_RECORDS_TO_GATHER = 100
OPEN_LIBRARY_RECORDS_TO_GATHER = 100
API_CALL_LIMIT = 25
USER_AGENT = 'BookTrendAnalyzer (jbachrach36@gmail.com)'


# SET UP DATABASE
def set_up_database(db_name):
    """
    Sets up a connection to an SQLite database.

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
    Creates the 'Books' and 'GenreLookup' tables in the database.

    Args:
        cur: the cursor object
        conn: the connection object
    """
    # Create GenreLookup table for storing genre names and their IDs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS GenreLookup (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT UNIQUE NOT NULL
        )
    ''')

    # Create Books table for storing book metadata
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            author TEXT,
            publish_date INTEGER NOT NULL,
            source_api TEXT NOT NULL,
            genre_id INTEGER,
            FOREIGN KEY (genre_id) REFERENCES GenreLookup(genre_id)
        )
    ''')
    conn.commit()


# GET GOOGLE BOOKS JSON
def get_google_books_json(query, max_results=API_CALL_LIMIT, start_index=0):
    # Placeholder for Google Books API call
    pass


# GET OPEN LIBRARY JSON
def get_openlibrary_json(genre, limit=API_CALL_LIMIT, page=1):
    """
    Fetches JSON data from Open Library API.

    Args:
    genre (str, optional): Search by genre.
    limit (int): Results per page.
    page (int): Page number.

    Returns:
    dict or None: API response JSON or None if failed.
    """
    params = {
        'limit': limit,
        'page': page,
        'format': 'json',
        # subject is how  to handle genre with the API
        'subject': genre
    }
    headers = {'User-Agent': USER_AGENT}
    try:
        # Formulate URL. Example: https://openlibrary.org/search.json?limit=10&page=1&format=json&subject=science+fiction
        response = requests.get(OPEN_LIBRARY_BASE_URL, params=params, headers=headers)
        # Get status
        response.raise_for_status()
        return response.json()
    # General exceptions
    except requests.exceptions.RequestException as e:
        print(f"Open Library API Error: {e}")
        if response is not None:
            print(f"Response Status Code: {response.status_code}")
            try:
                print(f"Response Text: {response.text}")
            except:
                print("Could not parse response text.")
        return None


# PROCESS GOOGLE BOOKS DATA
def process_google_books_data(cur, conn, data, target_genres, genre_dict):
    # Placeholder for processing Google Books API data
    pass


# PROCESS OPEN LIBRARY DATA
def process_open_library_data(cur, conn, data, target_genres, genre_dict):
    """
    Processes and stores Open Library data.

    Args:
        cur: Cursor object.
        conn: Connection object.
        data: API response JSON.
        target_genres: List of genres being searched for. The first genre in this list
                        will be used as the default.
        genre_dict (dict): A dictionary mapping genre names to genre_ids.

    Returns:
        int: Number of records inserted.
    """
    inserted_count = 0

    # Check if 'docs' exist in the response. 'docs' holds the actual results
    if data and 'docs' in data:
        for doc in data['docs']:
            title = doc.get('title')
            authors_data = doc.get('author_name')
            author = ', '.join(authors_data) if authors_data else None
            publish_date = doc.get('first_publish_year')

            # Skip record if required fields are missing
            if not (title and publish_date):
                #print(f"Skipping record due to missing title or publish_date: {doc}")
                continue

            # Ensure publish_date is a valid integer
            try:
                publish_year = int(publish_date)
            except (ValueError, TypeError):
                #print(f"Skipping record due to invalid publish_date: {publish_date}")
                continue

            # First target genre target genre
            if target_genres:
                matched_genre = target_genres[0]
            else:
                print("Warning: No target genres provided, skipping record.")
                continue

            # Insert record using genre_dict
            try:
                genre_id = genre_dict.get(matched_genre)
                if genre_id is not None:
                    # Insert book record into Books table
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO Books
                        (title, author, publish_date, source_api, genre_id)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (title, author, publish_year, 'Open Library', genre_id)
                    )
                    inserted_count += 1
                    #print(f"Inserted record: {title}, Genre: {matched_genre}, Genre ID: {genre_id}, Year: {publish_year}")
                else:
                    print(f"Error: Could not find genre_id for {matched_genre}")

            # Exception raised when the relational integrity of the database is affected, e.g. a foreign key check fails. from sqlite3 documentation
            except sqlite3.IntegrityError as e:
                print(f"Database Integrity Error: {e}")
                continue

        conn.commit()
    else:
        print("No valid data found in the API response.")

    return inserted_count


# GATHER GOOGLE BOOKS DATA
def gather_google_books_data(cur, conn, query, num_records, target_genres, genre_dict):
    # Placeholder for gathering Google Books data
    pass


# GATHER OPEN LIBRARY DATA
def gather_open_library_data(cur, conn, num_records, target_genres, genre_dict):
    # Loop through eah genre that was selected in main, and populate table
    for genre in target_genres:
        fetched_count = 0
        page = 1
        # Tracks records inserted for this genre
        genre_inserted_total = 0
        print(f"Gathering data from Open Library for genre: '{genre}'")

        while fetched_count < num_records and genre_inserted_total < num_records:
            # Call Open Library API
            results = get_openlibrary_json(genre, page=page)

            # If results are valid and contain 'docs'
            if results and 'docs' in results and results['docs']:
                # Process the data for this page
                inserted_now = process_open_library_data(cur, conn, results, [genre], genre_dict)
                #print(f"Inserted {inserted_now} records for genre '{genre}' on page {page}.")
                genre_inserted_total += inserted_now
                fetched_count += len(results['docs'])
                page += 1

                # Stop if API limit reached or no more results
                if inserted_now < API_CALL_LIMIT or results.get('numFound', 0) <= fetched_count:
                    break
            else:
                print(f"No 'docs' found for genre '{genre}' on page {page}.")
                break

        print(f"Finished gathering {genre_inserted_total} records from Open Library for genre: '{genre}'")