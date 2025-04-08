# main.py
import sqlite3
import os
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
    



    # TEST CODE (Temporary):
    # testing set_up_database and create_tables
    cur, conn = dg.set_up_database(DATABASE_NAME)
    dg.create_tables(cur, conn)
    conn.close()


if __name__ == "__main__":
    main()