# data_analysis.py
import sqlite3
import matplotlib.pyplot as plt
import os
import csv

# GLOBAL CONSTANTS (kept consistent across the other files)
DATABASE_NAME = "book_trends.db"
VISUALIZATION_OUTPUT_DIR = "visualizations"
TOPIC_FREQUENCY_OUTPUT_FILE = "topic_frequency.csv"
TOPIC_PERCENTAGE_CHANGE_OUTPUT_FILE = "topic_percentage_change.csv"
ALL_COMMON_GENRES = [
    "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance",
    "Historical Fiction", "Contemporary Fiction", "Young Adult",
    "Biography", "Autobiography", "Memoir", "Cookbook", "Travel",
    "Poetry", "Drama", "Horror"
]



# ANALYZE TOPIC TRENDS
def analyze_topic_trends(cur, conn, target_genres):
    pass



# CALCULATE TOPIC FREQUENCY
def calculate_topic_frequency(cur, output_file, target_genres):
    pass



# CALCULATE PERCENTAGE CHANGE
def calculate_percentage_change(cur, output_file, target_genres):
    pass



# VISUALIZE TOPIC FREQUENCY
def visualize_topic_frequency(cur, output_dir, target_genres):
    pass



# VISUALIZE GENRE DISTRIBUTION
def visualize_genre_distribution(cur, output_dir, target_genres):
    pass