# utility.py
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
    "Science Fiction", "Fantasy", "Mystery",
    "Thriller", "Romance", "Horror"
]
VISUALIZATION_OUTPUT_DIR = "visualizations"


# PRESENT API CHOICES
def present_api_choices():
    """Prompts the user to choose an API source for book data."""
    print("Choose which API to gather book data from:")
    print("1. Open Library")
    print("2. Google Books")
    while True:
        try:
            api_number = int(input("Enter 1 or 2: "))
            if api_number in [1, 2]:
                return api_number
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")




# SET UP DATABASE
def set_up_database():
    """
    Creates/connects to the database of DATABASE_NAME
    """
    cur, conn = dg.set_up_database(DATABASE_NAME)
    return cur, conn


# GET OR ADD GENRE
def get_or_add_genre(cur, conn, genre_name):
    """
    Get the genre_id for 'genre_name', adding it if not present. Ensures no ID gaps.
    Returns the genre_id as int.
    """
    cur.execute("SELECT genre_id FROM GenreLookup WHERE genre = ?", (genre_name,))
    response = cur.fetchone()
    if response:
        return response[0]
    cur.execute("INSERT INTO GenreLookup (genre) VALUES (?)", (genre_name,))
    conn.commit()
    return cur.lastrowid






# FULL RESET DATABASE
def full_reset_database(cur, conn):
    """
    Fully clears all records from the Books and GenreLookup tables
    and resets their auto-increment counters, WITHOUT DROPPING THE TABLES.
    """
    try:
        # Temporarily disable foreign key checks
        cur.execute("PRAGMA foreign_keys = OFF;")




        # Check if tables exist before attempting to delete
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Books';")
        if cur.fetchone():
             # Delete all rows from Books
            cur.execute("DELETE FROM Books;")
            # Reset the auto increment counter for Books
            cur.execute("DELETE FROM sqlite_sequence WHERE name='Books';")




        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GenreLookup';")
        if cur.fetchone():
            # Delete all rows from GenreLookup
            cur.execute("DELETE FROM GenreLookup;")
            # Reset the auto increment counter for GenreLookup
            cur.execute("DELETE FROM sqlite_sequence WHERE name='GenreLookup';")




        # Turn foreign key checks back on
        cur.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        print("Tables cleared and ID counters reset.")




    # Don't clear if there is nothing to clear. Operation error is a problem with the sql database operation
    # For general sqlite3 errors
    except sqlite3.Error as e:
        print(f"An error occurred during database reset: {e}")
        # Attempt to roll back changes if something went wrong mid-way
        conn.rollback()
        # Optionally re-enable foreign keys if they were turned off
        try:
            cur.execute("PRAGMA foreign_keys = ON;")
        # No error if connection is closed
        except:
             pass
       


       
def prompt_full_reset_database(cur, conn):
    """ Prompts the user if they want to clear the database before proceeding.
    """
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
    """ Presents the list of genres and prompts the user to select one.
    """
    print("Choose one genre to analyze:")
    for i, genre in enumerate(ALL_COMMON_GENRES):
        print(f"{i + 1}. {genre}")


    while True:
        try:
            genre_number = int(input("Enter the corresponding number of the genre you want to analyze (e.g., any single number from 1 to 6): "))
            if 1 <= genre_number <= len(ALL_COMMON_GENRES):
                return [ALL_COMMON_GENRES[genre_number - 1]]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(ALL_COMMON_GENRES)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")




def prompt_analyze_data():
    """
    Asks the user if they want to analyze and visualize the data.
    Returns True if yes, False if no.
    """
    while True:
        try:
            choice = input("Would you like to analyze and visualize the data? (y/n): ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")










# ENSURE GENRE EXISTS AND GET ID (Big changes here)
def ensure_genre_and_get_id(cur, conn, target_genre):
    """
    Ensures the target genre exists in GenreLookup.
    Adds it if it doesn't exist (auto-incrementing ID).
    Returns a dictionary that maps the genre name to its genre_id.
    """
    genre_dict = {}
    try:
        # Insert the genre if it doesn't exist. If it exists, this does nothing.
        cur.execute('INSERT OR IGNORE INTO GenreLookup (genre) VALUES (?)', (target_genre,))
        conn.commit()




        # Retrieve the genre_id (no matter if it was just inserted or already existed)
        cur.execute('SELECT genre_id FROM GenreLookup WHERE genre = ?', (target_genre,))
        result = cur.fetchone()




        if result:
            genre_id = result[0]
            genre_dict[target_genre] = genre_id
            print(f"Genre '{target_genre}' is in database with ID: {genre_id}.")
        else:
            print(f"Error: Could not retrieve genre_id for {target_genre} after insertion attempt.")
            conn.rollback()




    except sqlite3.Error as e:
        print(f"Database error while ensuring genre '{target_genre}': {e}")
        conn.rollback()
        return {}


    return genre_dict









