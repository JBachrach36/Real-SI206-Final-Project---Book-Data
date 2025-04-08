# data_gathering.py
import re
import os
import csv
import unittest
import requests
import matplotlib.pyplot as plt
import sqlite3
import json
from datetime import datetime
import my_keys


# API Keys
google_books_key = my_keys.GOOGLE_BOOKS_KEY
# No Open Library API Key needed

# GLOBAL CONSTANTS

# CREATE DATABASE
def set_up_database(db_name):
    pass

# CREATE TABLES
def create_tables(cur, conn):
    pass

# GET GOOGLE BOOKS JSON
def get_google_books_json():

    pass

# GET OPENLIBRARY JSON
def get_openlibrary_json():
    pass

# PROCESS GOOGLE BOOKS DATA
def process_google_books_data(cur, conn, data):
    pass

# PROCESS OPEN LIBRARY DATA
def process_open_library_data(cur, conn, data):
    pass

# GATHER DATA FROM GOOGLE BOOKS
def gather_google_books_data():
    pass

# GATHER DATA FROM OPEN LIBRARY
def gather_open_library_data():
    pass

# ANALYZE TOPIC TRENDS
def analyze_topic_trends(cur, conn):
    pass

# CALCULATE TOPIC FREQUENCY OVER TIME
def calculate_topic_frequency():
    pass

# CALCULATE PERCENTAGE CHANGE IN TOPIC FREQUENCY
def calculate_percentage_change():
    pass

# VISUALIZE TOPIC FREQUENCY OVER TIME (LINE CHARTS)
def visualize_topic_frequency():
    pass

# VISUALIZE GENRE DISTRIBUTION OVER TIME (STACKED AREA CHART)
def visualize_genre_distribution(cur):
    pass

# Main
def main():
    pass

if __name__ == "__main__":
    main()