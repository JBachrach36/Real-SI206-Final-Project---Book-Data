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
VISUALIZATION_OUTPUT_DIR = "visualizations"

# MAIN
def main():
    """
    Operates all functions: data gathering, analysis, visualization.
    Gets user input for genres then calls the data gathering functions.
    Then calls analysis and visualization functions.
    """

    # Present genre choices to the user



    # Set up database connection (used by both gathering and analysis)



    # Create tables (moved here to ensure they exist before gathering)



    # Gather data

    # Commit after gathering all data




    # Analyze and visualize data


    # Close connection
    
    



    # TEST CODE (Temporary):
    # open_library_query = "books"
    # dg.gather_open_library_data(cur, conn, open_library_query, dg.OPEN_LIBRARY_RECORDS_TO_GATHER, target_genres)
    


if __name__ == "__main__":
    main()