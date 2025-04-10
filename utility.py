import re
import os
import csv
import unittest
import requests
import matplotlib.pyplot as plt
import sqlite3
import json
import data_gathering as dg
import data_analysis as da

# GLOBAL CONSTANTS (kept consistent across the other files)
DATABASE_NAME = "book_trends.db"
ALL_COMMON_GENRES = [
    "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance",
    "Historical Fiction", "Contemporary Fiction", "Young Adult",
    "Biography", "Autobiography", "Memoir", "Cookbook", "Travel",
    "Poetry", "Drama", "Horror"
]
VISUALIZATION_OUTPUT_DIR = "visualizations"


# SET UP DATABASE
def set_up_database():
    cur, conn = dg.set_up_database(DATABASE_NAME)
    return cur, conn


# FULL RESET DATABASE
def full_reset_database(cur, conn):
    """
    Fully clears all records from the Books and GenreLookup tables
    and resets their auto-increment counters, WITHOUT DROPPING THE TABLES.
    """
    try:
        # Temporarily disable foreign key checks
        cur.execute("PRAGMA foreign_keys = OFF;")

        # Delete all rows from child Books (if it exists)
        cur.execute("DELETE FROM Books;")
        # Delete all rows from GenreLookup (if it exists)
        cur.execute("DELETE FROM GenreLookup;")

        # Reset the auto increment counters in sqlite_sequence (if it exists)
        cur.execute("DELETE FROM sqlite_sequence WHERE name='Books';")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='GenreLookup';")

        # Turn foreign key checks back on
        cur.execute("PRAGMA foreign_keys = ON;")

        conn.commit()
        print("Tables cleared and ID counters reset.")
    # Don't clear if there is nothing to clear. Operation error is a problem with the sql database operation
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("Tables do not exist yet. Skipping reset.")
        else:
            # If it's a different OperationalError, still show the error
            raise e


# PRESENT GENRE CHOICES
def present_genre_choices():
    print("Choose up to 10 genres to analyze:")
    for i, genre in enumerate(ALL_COMMON_GENRES):
        print(f"{i + 1}. {genre}")
    print("Choose up to 10 genres to analyze:")

    # Ensure the user selected 10 or less genres
    selected_indices = input("Enter the numbers of the genres you want to analyze (e.g., 1 2 3): ")
    try:
        # Split the string input into individual elements
        indices_str = selected_indices.split()

        # Convert string indices to integers
        selected_indices = []
        for index_str in indices_str:
            index = int(index_str) - 1
            selected_indices.append(index)

        # Validate indices
        valid_indices = True
        for index in selected_indices:
            if index < 0 or index >= len(ALL_COMMON_GENRES):
                valid_indices = False
                break

        # Check if number of selections is valid
        if not valid_indices or len(selected_indices) > 10:
            raise ValueError

        # Create target_genres list from selected indices
        target_genres = []
        for index in selected_indices:
            target_genres.append(ALL_COMMON_GENRES[index])

    except ValueError:
        print("Invalid input. Analyzing first 10 genres.")
        target_genres = ALL_COMMON_GENRES[:10]

    return target_genres


# INSERT TARGET GENRES
def insert_target_genres(cur, conn, target_genres):
    # Populate genre_dict with the genre name and its corresponding ID
    genre_dict = {}
    for genre in target_genres:
        cur.execute('INSERT OR IGNORE INTO GenreLookup (genre) VALUES (?)', (genre,))
        conn.commit()
        cur.execute('SELECT genre_id FROM GenreLookup WHERE genre = ?', (genre,))
        genre_id = cur.fetchone()[0]
        genre_dict[genre] = genre_id

    # Gather data from both APIs
    # TODO Uncomment these when I make the gather google books data function 
    # google_query = "books"
    # dg.gather_google_books_data(
    #     cur, conn, google_query,
    #     dg.GOOGLE_BOOKS_RECORDS_TO_GATHER,
    #     target_genres,
    #     genre_dict
    # )
    dg.gather_open_library_data(
        cur, conn,
        dg.OPEN_LIBRARY_RECORDS_TO_GATHER,
        target_genres,
        genre_dict
    )

    return genre_dict
