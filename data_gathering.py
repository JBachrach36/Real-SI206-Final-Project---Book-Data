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
    # GenreLookup Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS GenreLookup (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT UNIQUE NOT NULL
        )
    ''')

    # Books Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            author TEXT,
            publish_date TEXT NOT NULL,
            source_api TEXT NOT NULL,
            subject_categories TEXT,
            genre_id INTEGER,
            FOREIGN KEY (genre_id) REFERENCES GenreLookup(genre_id)
        )
    ''')
    conn.commit()




# GET GOOGLE BOOKS JSON
def get_google_books_json(query, max_results=API_CALL_LIMIT, start_index=0):
    pass



# GET OPEN LIBRARY JSON
def get_openlibrary_json(subject, limit=API_CALL_LIMIT, page=1):
    """
    Fetches JSON data from Open Library API.

    Args:
    subject (str, optional): Search by subject.
    limit (int): Results per page.
    page (int): Page number.

    Returns:
    dict or None: API response JSON or None if failed.
    """
    params = {
        'limit': limit,
        'page': page,
        'format': 'json',
        'subject': subject
    }
    headers = {'User-Agent': USER_AGENT}
    try:
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
def process_google_books_data(cur, conn, data, target_genres):
    pass



# PROCESS OPEN LIBRARY DATA
def process_open_library_data(cur, conn, data, target_genres):
    """
    Processes and stores Open Library data.

    Args:
    cur: Cursor object.
    conn: Connection object.
    data: API response JSON.
    target_genres: List of genres to match.

    Returns:
    int: Number of records inserted.
    """
    # Keeps track of number of inserted records
    inserted_count = 0  

    if data and 'docs' in data:
        for doc in data['docs']:
            # Get the relevant info for the tables
            title = doc.get('title')
            authors_data = doc.get('author_name')
            author = ', '.join(authors_data) if authors_data else None
            publish_date = doc.get('first_publish_year')
            subjects = doc.get('subject')

            # Only continue if title, publish_date, and subjects are available
            if title and publish_date and subjects:
                publish_date = str(publish_date)  # Convert year to string

                # IMPORTANT check if any subject matches a target genre
                for subject in subjects:
                    cleaned_subject = subject.strip().lower()

                    for genre in target_genres:
                        # Regex word boundary to avoid partial matches
                        pattern = r'\b' + re.escape(genre.lower()) + r'\b'
                        if re.search(pattern, cleaned_subject):
                            try:
                                # Insert genre into GenreLookup if it is not already there
                                cur.execute(
                                    'INSERT OR IGNORE INTO GenreLookup (genre) VALUES (?)', 
                                    (genre,),
                                )
                                # get the genre_id to use in the Books table
                                cur.execute(
                                    """
                                    SELECT genre_id
                                    FROM GenreLookup
                                    WHERE genre = ? 
                                    """, 
                                    (genre,),
                                )
                                genre_id = cur.fetchone()[0]

                                # Insert the book info into the Books table
                                cur.execute(
                                    """
                                    INSERT OR IGNORE INTO Books
                                    (title, author, publish_date, source_api, subject_categories, genre_id)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    """,
                                    (title, author, publish_date, 'Open Library', subject, genre_id))

                                inserted_count += 1

                                # Commit and return early if the API call limit is reached
                                if inserted_count >= API_CALL_LIMIT:
                                    conn.commit()
                                    return inserted_count
                            except sqlite3.IntegrityError:
                                # Don't add any records that violate the database’s constraints
                                pass
                            # Don't check any more genres if a match is found
                            break 

        conn.commit()
    return inserted_count




# GATHER GOOGLE BOOKS DATA
def gather_google_books_data(cur, conn, query, num_records, target_genres):
    pass



# GATHER OPEN LIBRARY DATA
def gather_open_library_data(cur, conn, num_records, target_genres):
    """
    Gathers and stores book data from Open Library API using subject search.

    Args:
    cur: Cursor object.
    conn: Connection object.
    num_records: Max number of records to insert per genre.
    target_genres: List of genres to filter.
    """
    total_inserted = 0
    for genre in target_genres:
        fetched_count = 0
        page = 1
        print(f"Gathering data from Open Library for subject: '{genre}'")
        
        # Initialize counters so API isn't used too much and not too many records are inserted at once
        # fetched_count is used to track the number of records fetched in total
        # total_inserted tracks how many records were actually inserted into the database
        while fetched_count < num_records and total_inserted < num_records:
            results = get_openlibrary_json(subject=genre, page=page)
            
            # Make sure API call was successful and that the 'docs' key is in the results
            if results and 'docs' in results:
                # Insert the records for the current genre and page of results
                inserted_now = process_open_library_data(cur, conn, results, [genre])
                total_inserted += inserted_now
                fetched_count += len(results['docs'])
                page += 1
                
                # Break the loop if the API call limit is reached or if there are no more records to fetch
                if inserted_now < API_CALL_LIMIT or results.get('numFound', 0) <= fetched_count:
                    break
            else:
                # If the API call failed or 'docs' isn't in the response, stop fetching
                break
        
        # Finished gathering data for this genre
        print(f"Finished gathering {total_inserted} records from Open Library for subject: '{genre}'")