# main.py
import sqlite3
import os
import data_gathering as dg
import data_analysis as da
import utility as u


# GLOBAL CONSTANTS (kept consistent across the other files)
DATABASE_NAME = "book_trends.db"
ALL_COMMON_GENRES = [
    "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance",
    "Historical Fiction", "Contemporary Fiction", "Young Adult",
    "Biography", "Autobiography", "Memoir", "Cookbook", "Travel",
    "Poetry", "Drama", "Horror"
]
VISUALIZATION_OUTPUT_DIR = "visualizations"


# MAIN
def main():
    """
    Operates all functions: data gathering, analysis, visualization.
    Gets user input for genres then calls the data gathering functions.
    Then calls analysis and visualization functions.
    """

    # Present genre choices to the user
    target_genres = u.present_genre_choices()

    # TODO Prompt user to select API

    # Set up database connection (used by both gathering and analysis)
    cur, conn = u.set_up_database()

    # Prompt user to clear data and reset IDs
    u.prompt_full_reset_database(cur, conn)

    # Create tables (moved here to ensure they exist before gathering)
    dg.create_tables(cur, conn)

    # Insert all target genres into GenreLookup first
    # Not used in main, but essential in other functions to populate the database
    genre_dict = u.insert_target_genres(cur, conn, target_genres)

    # Commit after gathering all data
    conn.commit()

    # Analyze and visualize data
    # TODO Call necessary functions for data analysis
    
    # Close connection
    conn.close()


if __name__ == "__main__":
    main()
