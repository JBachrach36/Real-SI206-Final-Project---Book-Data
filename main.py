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


    # Present genre choices to the user (gets a list with one genre)
    target_genres_list = u.present_genre_choices()
    if not target_genres_list:
        print("No genre selected. Exiting.")
        return
    target_genre = target_genres_list[0]


    # Prompt user to select API
    api_choice = u.present_api_choices()


    # Set up database connection (used by both gathering and analysis)
    cur, conn = u.set_up_database()


    # Prompt user to clear data and reset IDs
    u.prompt_full_reset_database(cur, conn)


    # Create tables
    dg.create_tables(cur, conn)


    # Ensure genre exists and get its id. Modified to make the ids increment properly
    genre_id = u.get_or_add_genre(cur, conn, target_genre)
    genre_dict = {target_genre: genre_id}
    print(f"Genre '{target_genre}' is in database with ID: {genre_id}.")






    if not genre_dict:
        print(f"Could not process genre: {target_genre}. Exiting.")
        conn.close()
        return
   
    if api_choice == 1:
        print(f"Attempting to gather {dg.OPEN_LIBRARY_RECORDS_TO_GATHER} new records for '{target_genre}' from Open Library")
        dg.gather_open_library_data(
            cur, conn,
            dg.OPEN_LIBRARY_RECORDS_TO_GATHER,
            target_genre,
            genre_dict
        )
    elif api_choice == 2:
        print(f"Attempting to gather {dg.GOOGLE_BOOKS_RECORDS_TO_GATHER} new records for '{target_genre}' from Google Books")
        dg.gather_google_books_data(
            cur, conn,
            dg.GOOGLE_BOOKS_RECORDS_TO_GATHER,
            target_genre,
            genre_dict
        )






    # Commit after gathering all data
    print("Committing gathered data")
    conn.commit()


    # Analyze and visualize data
    # TODO Call necessary functions for data analysis
    #print("Analysing and visualiing data")
   
    # Close connection
    print("Closing database connection.")
    conn.close()




if __name__ == "__main__":
    main()



