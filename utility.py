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
        
def prompt_full_reset_database(cur, conn):
    while True:
        try:
            user_input = input("Do you want to fully clear the database first? (y/n): ").strip().lower()
            if user_input == 'y':
                full_reset_database(cur, conn)
                break
            elif user_input == 'n':
                print("Skipping database reset.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")

    



# PRESENT GENRE CHOICES
def present_genre_choices():
    print("Choose one genre to analyze:")
    for i, genre in enumerate(ALL_COMMON_GENRES):
        print(f"{i + 1}. {genre}")

    while True:
        try:
            genre_number = int(input("Enter the corresponding number of the genre you want to analyze (e.g., any single number from 1 to 16): "))
            if 1 <= genre_number <= len(ALL_COMMON_GENRES):
                return [ALL_COMMON_GENRES[genre_number - 1]]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(ALL_COMMON_GENRES)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")





# INSERT TARGET GENRES
def insert_target_genre(cur, conn, target_genre):
    # Populate genre_dict with the genre name and its corresponding ID
    genre_dict = {}
    for genre in target_genre:
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
    #     target_genre,
    #     genre_dict
    # )
    dg.gather_open_library_data(
        cur, conn,
        dg.OPEN_LIBRARY_RECORDS_TO_GATHER,
        target_genre,
        genre_dict
    )

    return genre_dict
