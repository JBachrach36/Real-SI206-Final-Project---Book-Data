# data_analysis.py
import sqlite3
import matplotlib.pyplot as plt
import csv
import os
import pandas as pd


# CONSTANTS
DATABASE_NAME = "book_trends.db"
VISUALIZATION_OUTPUT_DIR = "visualizations"
# csv output
CALCULATIONS_OUTPUT_DIR = "calculations"
CALCULATION_FILENAME_TEMPLATE = "{genre}_analysis_results.csv"
PLOT_FILENAME_TEMPLATE = "{genre}_{plot_type}.png"


# Calculation Functions


# CALCULATE BOOKS PER DECADE
def calculate_books_per_decade(cur, target_genre_id):
    """
    Calculates the number of books published per decade for a specific genre.


    Args:
        cur: Database cursor object.
        target_genre_id (int): The ID of the genre to analyze.


    Returns:
        dict: A dictionary mapping decade start year (int) to book count (int),
              or None if an error occurs or no data is found.
    """
    try:
        cur.execute("""
            SELECT Books.publish_date
            FROM Books
            JOIN GenreLookup ON Books.genre_id = GenreLookup.genre_id
            WHERE Books.genre_id = ? AND Books.publish_date IS NOT NULL
        """, (target_genre_id,))


        years = []
        # Fetch all results
        all_rows = cur.fetchall()


        # Iterate through each row returned from the database
        for row in all_rows:
        # Check if the first element in the row exists and is an integer
            if row and isinstance(row[0], int):
                # Append it to the years list if it's an integer
                years.append(row[0])


        if not years:
            print(f"No valid publication year data found for genre_id {target_genre_id}.")
            return None


        # Calculate decade counts
        decade_counts = {}
        for year in years:
            if 1000 <= year <= 2100:
               decade = (year // 10) * 10
               decade_counts[decade] = decade_counts.get(decade, 0) + 1
            else:
                 print(f"Skipping invalid or out-of-range year: {year}")


        return decade_counts


    except sqlite3.Error as e:
        print(f"Database error during decade calculation for genre_id {target_genre_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during decade calculation: {e}")
        return None




# CALCULATE TOP AUTHORS
def calculate_top_authors(cur, target_genre_id, top_n=10):
    """
    Calculates the top 10 most frequent authors for a specific genre.


    Args:
        cur: Database cursor object.
        target_genre_id (int): The ID of the genre to analyze.
        top_n (int): The number of top authors to return.


    Returns:
        list: A list of tuples, where each tuple is (author_name, book_count),
              sorted by book_count descending. Returns None if an error occurs.
    """
    try:
        cur.execute("""
            SELECT Books.author, COUNT(Books.book_id) as book_count
            FROM Books
            JOIN GenreLookup ON Books.genre_id = GenreLookup.genre_id
            WHERE Books.genre_id = ? AND Books.author IS NOT NULL AND Books.author != ''
            GROUP BY Books.author
            ORDER BY book_count DESC
            LIMIT ?
        """, (target_genre_id, top_n,))


        top_authors = cur.fetchall()


        if not top_authors:
             print(f"No author data found for genre_id {target_genre_id}.")
             return None


        return top_authors


    except sqlite3.Error as e:
        print(f"Database error during author calculation for genre_id {target_genre_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during author calculation: {e}")
        return None




# OUTPUT TO FILE
def write_calculations_to_csv(decade_data, author_data, filename, output_dir):
    """
    Writes the calculated decade and author data to a single CSV file.


    Args:
        decade_data (dict): Dictionary of decade counts {decade: count}.
        author_data (list): List of top author tuples [(author, count)].
        filename (str): The name for the output CSV file.
        output_dir (str): The directory to save the CSV file in.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)


    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
           
            # Write Decade Data
            writer.writerow(['*** Books Per Decade ***'])
            writer.writerow(['Decade Start Year', 'Book Count'])
            if decade_data:
                 # Sort decades for consistent output
                for decade, count in sorted(decade_data.items()):
                    writer.writerow([decade, count])
            else:
                writer.writerow(['No data available', ''])
           
            # Add a separator row
            writer.writerow([])
           
            # Write Author Data
            writer.writerow([f'*** Top {len(author_data) if author_data else 0} Authors ***'])
            writer.writerow(['Author', 'Book Count'])
            if author_data:
                for author, count in author_data:
                    writer.writerow([author, count])
            else:
                 writer.writerow(['No data available', ''])


        print(f"Calculation results written successfully to {filepath}")


    # file writing error
    except IOError as e:
        print(f"Error writing calculation results to CSV file {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")


# Visualization Functions


def plot_books_per_decade(decade_data, target_genre, filename, output_dir):
    """
    Creates and saves a bar chart showing books published per decade.


    Args:
        decade_data (dict): Dictionary mapping decade start year to count.
        target_genre (str): The name of the genre being plotted.
        filename (str): The name for the output image file.
        output_dir (str): The directory to save the plot image in.
    """
    if not decade_data:
        print("No decade data available to plot.")
        return


    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
   
    # Prepare data for plotting
    decades = sorted(decade_data.keys())
    counts = [decade_data[d] for d in decades]
    # Create labels like "1980s", "1990s" etc
    decade_labels = [f"{d}s" for d in decades]


    plt.figure(figsize=(10, 6))
    plt.bar(decade_labels, counts, color='skyblue')
   
    plt.xlabel("Decade")
    plt.ylabel("Number of Books Published")
    plt.title(f"Books Published per Decade in '{target_genre}' Genre")
     # Rotate labels if many decades
    plt.xticks(rotation=45, ha='right')
     # Adjust layout to prevent labels overlapping
    plt.tight_layout()
   
    try:
        plt.savefig(filepath)
        print(f"Decade distribution bar chart saved to {filepath}")
        plt.close()
    except Exception as e:
        print(f"Error saving decade plot to {filepath}: {e}")


# PLOT TOP AUTHORS
def plot_top_authors_pie(author_data, target_genre, filename, output_dir, max_slices=5):
    """
    Creates and saves a standard pie chart showing the distribution of books
    among top authors, similar to the provided example.
    Groups smaller slices into 'Others' for readability.


    Args:
        author_data (list): List of top author tuples [(author, count)].
        target_genre (str): The name of the genre being plotted.
        filename (str): The name for the output image file.
        output_dir (str): The directory to save the plot image in.
        max_slices (int): Maximum number of individual author slices before grouping.
    """
    if not author_data:
        print("No author data available to plot.")
        return


    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)


    labels = [item[0] for item in author_data]
    counts = [item[1] for item in author_data]


    # Group smaller slices if the total number of authors exceeds max_slices
    if len(labels) > max_slices:
        top_labels = labels[:max_slices-1]
        top_counts = counts[:max_slices-1]
        others_count = sum(counts[max_slices-1:])
        if others_count > 0:
             top_labels.append('Others')
             top_counts.append(others_count)
        labels = top_labels
        counts = top_counts


    plt.figure(figsize=(10, 8))


    wedges, texts, autotexts = plt.pie(
        counts,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.6,
        labeldistance=1.1,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )


    plt.legend(wedges, labels, title="Authors", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))


    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(10)


    plt.title(f"Book Distribution by Top Authors in '{target_genre}' Genre", pad=20, fontsize=14)
    plt.axis('equal')
    plt.tight_layout(rect=[0, 0, 0.75, 1])


    try:
        plt.savefig(filepath)
        print(f"Top authors pie chart saved to {filepath}")
        plt.close()
    except Exception as e:
        print(f"Error saving authors pie chart to {filepath}: {e}")


# PLOT TOP AUTHORS
def plot_top_authors_bar(author_data, target_genre, filename, output_dir):
    """
    Creates and saves a vertical bar chart for the top authors and their book counts.


    Args:
        author_data (list): List of top author tuples [(author, count)].
        target_genre (str): The name of the genre being plotted.
        filename (str): The name for the output image file.
        output_dir (str): The directory to save the plot image in.
    """
    if not author_data:
        print("No author data available to plot.")
        return


    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)


    authors = [item[0] for item in author_data]
    counts = [item[1] for item in author_data]


    plt.figure(figsize=(12, 7))
    bars = plt.bar(authors, counts, color='lightcoral')


    plt.xlabel("Author")
    plt.ylabel("Number of Books")
    plt.title(f"Top {len(authors)} Authors by Book Count in '{target_genre}' Genre")
    plt.xticks(rotation=60, ha='right', fontsize=9)
    plt.bar_label(bars, padding=3, fontsize=8)
    plt.tight_layout()


    try:
        plt.savefig(filepath)
        print(f"Top authors bar chart saved to {filepath}")
        plt.close()
    except Exception as e:
        print(f"Error saving authors bar chart to {filepath}: {e}")




# Run Analysis (used in main)




# RUN ANALYSIS AND VISUALIZATIONS
def run_analysis_and_visualizations(cur, target_genre, target_genre_id):
    """
    Runs all data analysis calculations and generates visualizations for the target genre.


    Args:
        cur: Database cursor object.
        target_genre (str): The name of the genre being analyzed (for labels/filenames).
        target_genre_id (int): The ID of the genre to filter data by.
    """
    print(f"\n*** Starting Analysis for Genre: {target_genre} (ID: {target_genre_id}) ***")


    # 1. Calculate Books per Decade
    print("Calculating books per decade...")
    decade_counts = calculate_books_per_decade(cur, target_genre_id)
    if decade_counts:
         print(f"Found data for {len(decade_counts)} decades.")
    else:
         print("No decade data found or error occurred.")


    # 2. Calculate Top 10 Authors
    print("Calculating top 10 authors...")
    top_authors = calculate_top_authors(cur, target_genre_id, top_n=10)
    if top_authors:
         print(f"Found top {len(top_authors)} authors.")
    else:
         print("No author data found or error occurred.")


    # 3. Write Calculations to CSV
    safe_genre_name = target_genre.replace(' ', '_').lower()
    csv_filename = CALCULATION_FILENAME_TEMPLATE.format(genre=safe_genre_name)
    print(f"Writing calculations to {csv_filename}...")
    write_calculations_to_csv(decade_counts, top_authors, csv_filename, CALCULATIONS_OUTPUT_DIR)


    # 4. Generate Visualizations
    print("Generating visualizations...")


    # Plot 1: Books per Decade (Bar Chart)
    decade_plot_filename = PLOT_FILENAME_TEMPLATE.format(genre=safe_genre_name, plot_type="decade_distribution")
    plot_books_per_decade(decade_counts, target_genre, decade_plot_filename, VISUALIZATION_OUTPUT_DIR)


    # Plot 2: Top Authors (Pie Chart)
    author_pie_filename = PLOT_FILENAME_TEMPLATE.format(genre=safe_genre_name, plot_type="top_authors_pie")
    plot_top_authors_pie(top_authors, target_genre, author_pie_filename, VISUALIZATION_OUTPUT_DIR)


    # Plot 3: Top Authors (Bar Chart)
    author_bar_filename = PLOT_FILENAME_TEMPLATE.format(genre=safe_genre_name, plot_type="top_authors_bar")
    plot_top_authors_bar(top_authors, target_genre, author_bar_filename, VISUALIZATION_OUTPUT_DIR)


    print(f"*** Analysis Complete for Genre: {target_genre} ***")






