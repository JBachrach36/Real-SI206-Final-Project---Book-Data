# main.py
import sqlite3
import os
import data_gathering
import data_analysis

# GLOBAL CONSTANTS (kept consistent across the other files)
DATABASE_NAME = "book_trends.db"
ALL_COMMON_GENRES = [
    "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance",
    "Historical Fiction", "Contemporary Fiction", "Young Adult",
    "Biography", "Autobiography", "Memoir", "Cookbook", "Travel",
    "Poetry", "Drama", "Horror"
]

# MAIN
def main():
    """
    Operates all functions: data gathering, analysis, visualization.
    Gets user input for genres then calls the data gathering functions.
    Then calls analysis and visualization functions.
    """

    # Present genre choices to the user

    # Set up database connection (used by both gathering and analysis)

    # Gather data

    # Analyze and visualize data


    # Close connection
    pass


if __name__ == "__main__":
    main()