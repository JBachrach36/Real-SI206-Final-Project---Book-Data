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
GOOGLE_BOOKS_RECORDS_TO_GATHER = 25
OPEN_LIBRARY_RECORDS_TO_GATHER = 25
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
    # Explicitly enable foreign key constraints for this connection
    cur.execute("PRAGMA foreign_keys = ON;")
    return cur, conn




# CREATE TABLES
def create_tables(cur, conn):
    """
    Creates the 'Books' and 'GenreLookup' tables in the database.
    Args:
        cur: the cursor object
        conn: the connection object
    """
    try:
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
            author TEXT NOT NULL,
            publish_date INTEGER NOT NULL,
            source_api TEXT NOT NULL,
            genre_id INTEGER,
            FOREIGN KEY (genre_id) REFERENCES GenreLookup(genre_id) ON DELETE SET NULL
        )
        ''')
        conn.commit()
        print("Database tables created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating database tables: {e}")
        conn.rollback()




# GET GOOGLE BOOKS JSON
def get_google_books_json(genre, max_results=API_CALL_LIMIT, start_index=0):
    """
    Gets JSON data from Google Books API.
    Args:
        genre (str): Genre to filter by (used as part of the query string).
        max_results (int): Results per API call (max 40 for Google Books).
        start_index (int): The result index to start from (for pagination).


    Returns:
        dict or None: API response JSON or None if failed.
    """
    params = {
        "maxResults": max_results,
        "startIndex": start_index,
        "key": google_books_key,
    }
    # Subject is genre
    if genre:
        params["q"] = f"subject:{genre}"


    headers = {'User-Agent': USER_AGENT}
    try:
        # Example link: https://www.googleapis.com/books/v1/volumes?q=subject:Science+Fiction&maxResults=25&startIndex=0&key=MYKEY
        response = requests.get(GOOGLE_BOOKS_BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Google Books API Error: {e}")
        if response is not None:
            print(f"Response Status Code: {response.status_code}")
            try:
                print(f"Response Text: {response.text}")
            except Exception:
                print("Could not parse response text.")
        return None




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
        'subject': genre.lower().replace(" ", "+")
    }
    headers = {'User-Agent': USER_AGENT}
    try:
        # Formulate URL. Example: https://openlibrary.org/search.json?subject=science+fiction&limit=25&page=1&format=json
        response = requests.get(OPEN_LIBRARY_BASE_URL, params=params, headers=headers, timeout=15)
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
def process_google_books_data(cur, conn, data, target_genre, genre_dict, remaining_limit):
    """
    Processes and stores Google Books data. Records require title, author, and publish_date.
    Only inserts up to remaining_limit new unique records.
    Args:
        cur: Cursor object.
        conn: Connection object.
        data: API response JSON ('items' key should exist).
        target_genre (str): The genre being processed.
        genre_dict (dict): Dictionary mapping genre name to genre_id.
        remaining_limit (int): Max new records to add this call.
    Returns:
        int: Number of records inserted in this call
    """
    inserted_count = 0
    items = data.get("items")
    if not items:
        print("No 'items' found in Google Books API response.")
        return 0


    genre_id = genre_dict.get(target_genre)
    if genre_id is None:
        print(f"Error: Could not find genre_id for target genre '{target_genre}' in genre_dict.")
        return 0


    for item in items:
        if inserted_count >= remaining_limit:
            break
        volume_info = item.get("volumeInfo", {})
        title = volume_info.get("title")
        authors = volume_info.get("authors")
        author = ', '.join(authors) if authors else None
        # Google Books publishDate format: 'YYYY', 'YYYY-MM', 'YYYY-MM-DD'
        publish_date = volume_info.get("publishedDate")
        publish_year = None
        if publish_date:
            try:
                # Try to extract the year
                publish_year = int(str(publish_date)[:4])
            except (ValueError, TypeError):
                continue


        if not title or not author or not publish_year:
            continue


        try:
            # Only insert if this title does not already exist in the database
            cur.execute("SELECT 1 FROM Books WHERE title = ?", (title,))
            already_exists = cur.fetchone()
            if already_exists:
                continue


            cur.execute(
                """
                INSERT INTO Books
                (title, author, publish_date, source_api, genre_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, author, publish_year, 'Google Books', genre_id,)
            )
            inserted_count += 1
        except sqlite3.IntegrityError as e:
            print(f"Database Integrity Error processing '{title}': {e}")
            conn.rollback()
            continue
        except sqlite3.Error as e:
            print(f"Database Error processing '{title}': {e}")
            conn.rollback()
            continue


    if not items:
        print("No book records ('items') found in this page of the API response.")


    return inserted_count






# PROCESS OPEN LIBRARY DATA
def process_open_library_data(cur, conn, data, target_genre, genre_dict, remaining_limit):
    """
    Processes and stores Open Library data for a single target genre.
    Skips records if title, author, or a valid publish_date are missing.
    Inserts up to remaining_limit unique records only.
    Args:
        cur: Cursor object.
        conn: Connection object.
        data: API response JSON containing 'docs'.
        target_genre (str): The specific genre being searched for.
        genre_dict (dict): A dictionary mapping the target_genre name to its genre_id.
        remaining_limit (int): Max new records to add this call.
    Returns:
        int: Number of new records inserted in this batch.
    """
    # Gather open library data goes through the pages
    inserted_count = 0
    # Check if 'docs' exist in the response. 'docs' holds the actual results
    if not data or 'docs' not in data:
        print("No 'docs' key found in Open Library response data.")
        return 0


    genre_id = genre_dict.get(target_genre)
    if genre_id is None:
        print(f"Error: Could not find genre_id for target genre '{target_genre}' in genre_dict.")
        # Cannot continue without a valid genre_id
        return 0


    for doc in data['docs']:
        if inserted_count >= remaining_limit:
            break
        title = doc.get('title')
        authors_data = doc.get('author_name')
        # Handle potential list of authors
        author = ', '.join(authors_data) if authors_data else None
        # Use the first publish year
        publish_date = doc.get('first_publish_year')


        # Skip record if required fields are missing
        if not title or not author:
            continue


        # Ensure publish_date is a valid integer. Skip if not valid
        publish_year = None
        if publish_date:
            try:
                publish_year = int(publish_date)
            except (ValueError, TypeError):
                continue
        else:
            continue


        try:
            # Only insert if this title does not already exist in the database
            cur.execute("SELECT 1 FROM Books WHERE title = ?", (title,))
            already_exists = cur.fetchone()
            if already_exists:
                continue


            # Insert as truly new record
            cur.execute(
                """
                INSERT INTO Books
                (title, author, publish_date, source_api, genre_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, author, publish_year, 'Open Library', genre_id,)
            )
            inserted_count += 1


        except sqlite3.IntegrityError as e:
            # This might still occur if, for example, the UNIQUE constraint on title is violated
            print(f"Database Integrity Error processing '{title}': {e}")
            conn.rollback()
            continue
        except sqlite3.Error as e:
             print(f"Database Error processing '{title}': {e}")
             conn.rollback()
             continue


    if not data['docs']:
        print("No book records ('docs') found in this page of the API response.")


    return inserted_count




# GATHER GOOGLE BOOKS DATA
def gather_google_books_data(cur, conn, num_records_goal, target_genre, genre_dict):
    """
    Gathers a target number of unique book records from Google Books API for a specific genre.
    Args:
        cur: Cursor object.
        conn: Connection object.
        num_records_goal (int): The target number of new records to insert.
        target_genre (str): The specific genre to gather data for.
        genre_dict (dict): Dictionary mapping the genre name to its ID.
    """
    total_inserted_count = 0
    start_index = 0
    # Google books max is 40
    max_per_page = min(API_CALL_LIMIT, 40)


    # For safety, do not go over 30 pages
    max_pages_to_try = 30
    page_counter = 0


    print(f"Gathering data from Google Books for genre: '{target_genre}' (Target: {num_records_goal} new insertions)")


    while total_inserted_count < num_records_goal and page_counter < max_pages_to_try:
        remaining = num_records_goal - total_inserted_count
        # Don't ask for more than needed
        page_max = min(max_per_page, remaining)
        print(f"Requesting from index {start_index} for genre '{target_genre}' (API page {page_counter+1}), requesting up to {page_max}")
        results = get_google_books_json(genre=target_genre, max_results=page_max, start_index=start_index)
        if results and "items" in results:
            if not results["items"]:
                print(f"No more book records found for genre '{target_genre}' at index {start_index}.")
                break


            inserted_now = process_google_books_data(cur, conn, results, target_genre, genre_dict, remaining)
            if inserted_now > 0:
                total_inserted_count += inserted_now
                conn.commit()
            else:
                print(f"No new records inserted from start_index {start_index} (likely duplicates or missing data).")


            if total_inserted_count >= num_records_goal:
                break


            # Move to the next page
            start_index += page_max
            page_counter += 1
        else:
            print(f"Failed to retrieve valid data or no 'items' found for genre '{target_genre}' from index {start_index}. Stopping.")
            break


    if page_counter >= max_pages_to_try:
        print(f"Reached maximum page limit ({max_pages_to_try}) for Google Books requests.")


    print(f"Finished gathering from Google Books for genre: '{target_genre}'.")
    print(f"Total new records inserted in this run: {total_inserted_count}")






# GATHER OPEN LIBRARY DATA
def gather_open_library_data(cur, conn, num_records_goal, target_genre, genre_dict):
    """
    Gathers a target number of unique book records from Open Library API for a specific genre.
    Stops when `num_records_goal` new books have been inserted or the API runs out of results.
    Args:
        cur: Cursor object.
        conn: Connection object.
        num_records_goal (int): The target number of new records to insert for this run.
        target_genre (str): The specific genre to gather data for.
        genre_dict (dict): Dictionary mapping the genre name to its ID.
    """
    genre_inserted_total = 0
    page = 1
    # Safety limit
    max_pages = 30


    print(f"Gathering data from Open Library for genre: '{target_genre}' (Target: {num_records_goal} new insertions)")


    # Loop while we haven't met the goal and have not accessed too many pages
    while genre_inserted_total < num_records_goal and page <= max_pages:
        remaining = num_records_goal - genre_inserted_total
        print(f"Requesting page {page} for genre '{target_genre}', up to {remaining} inserts left.")
        results = get_openlibrary_json(target_genre, limit=API_CALL_LIMIT, page=page)


        # If results are valid and contain 'docs'
        if results and 'docs' in results:
            # Check if 'docs' list is empty
            if not results['docs']:
                print(f"No more book records found for genre '{target_genre}' on page {page}.")
                break


            # Process the data for this page. Pass the single target genre & the records remaining limit
            inserted_now = process_open_library_data(cur, conn, results, target_genre, genre_dict, remaining)


            if inserted_now > 0:
                # print(f"Successfully inserted {inserted_now} new records from page {page}.")
                genre_inserted_total += inserted_now
                conn.commit()
            else:
                print(f"No new records inserted from page {page} (likely duplicates or missing data).")


            if genre_inserted_total >= num_records_goal:
                break


            # Go to next page
            page += 1


        # API error or no 'docs'
        else:
            print(f"Failed to retrieve valid data or no 'docs' found for genre '{target_genre}' on page {page}. Stopping.")
            break


    # Check if max_pages limit was hit
    if page > max_pages:
        print(f"Reached maximum page limit ({max_pages}) for Open Library requests.")


    print(f"Finished gathering from Open Library for genre: '{target_genre}'.")
    print(f"Total new records inserted in this run: {genre_inserted_total}")





