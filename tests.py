import sqlite3
import os
import json
import data_gathering as dg
import data_analysis as da




def test_open_library_json():
    query = "self-help"  # Example query
    results = dg.get_openlibrary_json(query)

    if results:
        print("Open Library Data:")
        # use this form for json pretty print
        print(json.dumps(results, indent=4))
    else:
        print("Failed to retrieve Open Library data.")





if __name__ == "__main__":
    print('Now Testing Open Library Json code')
    test_open_library_json()


