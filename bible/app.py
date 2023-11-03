import sqlite3
import json
import random
from flask import Flask, request, jsonify
from datetime import datetime


# Global variables to store the current "Verse of the Day" and its date
current_verse_of_the_day = None
current_verse_date = None


# Configure application
app = Flask(__name__)

@app.route("/")
def index():
    return ('ggg')


# Verse of the Day function
@app.route('/api/bible/verses/day', methods=['GET'])
def get_verse_of_the_day():

    global current_verse_of_the_day
    global current_verse_date

    # Get the current date and time
    now = datetime.now()

    # If it's a new day, update the "Verse of the Day"
    if current_verse_date is None or now.date() > current_verse_date:
        # Establish a connection to the SQLite database
        conn = sqlite3.connect('bible.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, isolation_level=None, uri=True)

        # Create a cursor
        cursor = conn.cursor()

        # Execute a query to count the total number of verses in your database
        cursor.execute("SELECT COUNT(*) FROM verse;")
        total_verses = cursor.fetchone()[0]

        # Generate a random verse ID
        random_verse_id = random.randint(1, total_verses)

        # Execute a query to retrieve the random verse
        cursor.execute("SELECT * FROM verse WHERE id = ?;", (random_verse_id,))
        random_verse = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()
        conn.close()

        if random_verse is None:
            return jsonify({'error': 'Verse not found.'}), 404

        current_verse_of_the_day = {
            'id': random_verse[0],
            'chapter_id': random_verse[1],
            'osisID': random_verse[2],
            'vnumber': random_verse[3],
            '_text': random_verse[4]
        }
        current_verse_date = now.date()

    # Create a response dictionary
    response = {
        'result': current_verse_of_the_day
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Random Verse function
@app.route('/api/bible/verses/random', methods=['GET'])
def get_random_verse():
    # Generate a random verse ID within the range of your verses
    random_verse_id = random.randint(1, 31067)  # The total number of verses from the database is 31067

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, isolation_level=None, uri=True)
    cursor = conn.cursor()

    # Execute the SQL query to retrieve the random verse
    cursor.execute("SELECT * FROM verse WHERE id = ?;", (random_verse_id,))
    random_verse = cursor.fetchone()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    if not random_verse:
        return jsonify({'error': 'No random verse found.'}), 404

    # Convert the data to a dictionary
    verse_dict = {
        'id': random_verse[0],
        'chapter_id': random_verse[1],
        'osisID': random_verse[2],
        'vnumber': random_verse[3],
        '_text': random_verse[4]
    }

    # Create a response dictionary
    response = {
        'result': verse_dict
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Get Books
@app.route('/api/bible/books', methods=['GET'])
def get_books():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT * FROM book;")

    # Fetch all the records
    books = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    books_list = [{'id': row[0], 'name': row[1], 'osisID': row[2]} for row in books]

    # Create a response dictionary
    response = {
        'result': books_list
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Get Chapters
@app.route('/api/bible/chapters', methods=['GET'])
def get_chapters():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT * FROM chapter;")

    # Fetch all the records
    chapters = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    chapter_list = [{'id': row[0], 'book_id': row[1], 'cnumber': row[2]} for row in chapters]

    # Create a response dictionary
    response = {
        'result': chapter_list
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Get Verses by Book
@app.route('/api/bible/books/<int:book_id>/verses', methods=['GET'])
def get_verses_by_book(book_id):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query to get the first and last chapters
    cursor.execute("SELECT MIN(id), MAX(id) FROM chapter WHERE book_id = ?;", (book_id,))
    chapters = cursor.fetchone()

    # Check if chapters were found
    if not chapters:
        # Handle the case where no chapters were found for the given book_id
        cursor.close()
        conn.close()
        return jsonify({'message': 'No chapters found for this book_id'}), 404

    # Unpack the first and last chapter IDs
    first_chapter_id, last_chapter_id = chapters

    # Execute the SQL query to get verses
    cursor.execute("SELECT * FROM verse WHERE chapter_id BETWEEN ? AND ?;", (first_chapter_id, last_chapter_id))

    # Fetch all the records
    verses = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    verse_list = [{'id': row[0], 'chapter_id': row[1], 'osisID': row[2], 'vnumber': row[3], '_text': row[4]} for row in verses]

    # Create a response dictionary
    response = {
        'result': verse_list
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Get Chapters by Book
@app.route('/api/bible/books/<int:book_id>/chapters', methods=['GET'])
def get_chapters_by_book(book_id):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT * FROM chapter WHERE book_id = ?;", (book_id,))

    # Fetch all the records
    chapters = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    chapter_list = [{'id': row[0], 'book_id': row[1], 'cnumber': row[2]} for row in chapters]

    # Create a response dictionary
    response = {
        'result': chapter_list
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Get Verse by Chapter
@app.route('/api/bible/chapters/<int:chapter_id>/verses', methods=['GET'])
def get_verse_by_chapter(chapter_id):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT * FROM verse WHERE chapter_id = ?;", (chapter_id,))

    # Fetch all the records
    verses = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    verse_list = [{'id': row[0], 'chapter_id': row[1], 'osisID': row[2], 'vnumber': row[3], '_text': row[4]} for row in verses]

    # Create a response dictionary
    response = {
        'result': verse_list
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


# Search Verses
@app.route('/api/bible/verses/search', methods=['GET'])
def search_verses():
    # Get the search query from the request
    query = request.args.get('query')

    if not query:
        return jsonify({'error': 'Please provide a search query'}), 400

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query to search for verses containing the query
    cursor.execute("SELECT * FROM verse WHERE _text LIKE ?;", ('%' + query + '%',))

    # Fetch all the matching verses
    verses = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    verse_list = [{'id': row[0], 'chapter_id': row[1], 'osisID': row[2], 'vnumber': row[3], '_text': row[4]} for row in verses]

    # Create a response dictionary
    response = {
        'result': verse_list
    }

     # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


#Get Verse by Reference:
@app.route('/api/bible/verses/reference/<reference>', methods=['GET'])
def get_verse_by_reference(reference):
    # Split the reference into its components (Book, Chapter, and Verse)
    parts = reference.split(" ")
    if len(parts) < 2:
        return jsonify({'error': 'Invalid reference format. Use "Book Chapter:Verse".'}), 400

    book_name = parts[0]
    chapter_verse = parts[1]

    # Extract chapter and verse numbers
    chapter, verse = chapter_verse.split(":")
    chapter = int(chapter)
    verse = int(verse)

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, isolation_level=None, uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute a query to find the book by name
    cursor.execute("SELECT id FROM book WHERE name = ?;", (book_name,))
    book_id = cursor.fetchone()

    if book_id is None:
        return jsonify({'error': 'Book not found.'}), 404

    book_id = book_id[0]

    # Execute a query to find the chapter by book ID and chapter number
    cursor.execute("SELECT id FROM chapter WHERE book_id = ? AND chapter_number = ?;", (book_id, chapter))
    chapter_id = cursor.fetchone()

    if chapter_id is None:
        return jsonify({'error': 'Chapter not found.'}), 404

    chapter_id = chapter_id[0]

    # Execute a query to retrieve the requested verse
    cursor.execute("SELECT * FROM verse WHERE chapter_id = ? AND vnumber = ?;", (chapter_id, verse))
    requested_verse = cursor.fetchone()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    if requested_verse is None:
        return jsonify({'error': 'Verse not found.'}), 404

    # Convert the data to a dictionary
    verse_dict = {
        'id': requested_verse[0],
        'chapter_id': requested_verse[1],
        'osisID': requested_verse[2],
        'vnumber': requested_verse[3],
        '_text': requested_verse[4]
    }

    # Create a response dictionary
    response = {
        'result': verse_dict
    }

    # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


#Get Next Verse:
@app.route('/api/bible/verses/<int:verse_id>/next', methods=['GET'])
def get_next_verse(verse_id):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, isolation_level=None, uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query to get the next verse
    cursor.execute("SELECT * FROM verse WHERE id > ? ORDER BY id LIMIT 1;", (verse_id,))
    next_verse = cursor.fetchone()

    if not next_verse:
        return jsonify({'error': 'No next verse found.'}), 404

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a dictionary
    verse_dict = {
        'id': next_verse[0],
        'chapter_id': next_verse[1],
        'osisID': next_verse[2],
        'vnumber': next_verse[3],
        '_text': next_verse[4]
    }

    # Create a response dictionary
    response = {
        'result': verse_dict
    }

    # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


#Get Previous Verse:
@app.route('/api/bible/verses/<int:verse_id>/previous', methods=['GET'])
def get_previous_verse(verse_id):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, isolation_level=None, uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query to get the previous verse
    cursor.execute("SELECT * FROM verse WHERE id < ? ORDER BY id DESC LIMIT 1;", (verse_id,))
    previous_verse = cursor.fetchone()

    if not previous_verse:
        return jsonify({'error': 'No previous verse found.'}), 404

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a dictionary
    verse_dict = {
        'id': previous_verse[0],
        'chapter_id': previous_verse[1],
        'osisID': previous_verse[2],
        'vnumber': previous_verse[3],
        '_text': previous_verse[4]
    }

    # Create a response dictionary
    response = {
        'result': verse_dict
    }

    # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}




#Get Verses:
@app.route('/api/bible/verses', methods=['GET'])
def get_verses():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('bible.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, isolation_level=None, uri=True)

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT * FROM verse;")

    # Fetch all the records
    verses = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Convert the data to a list of dictionaries
    verse_list = [{'id': row[0], 'chapter_id': row[1], 'osisID': row[2], 'vnumber': row[3], '_text': row[4]} for row in verses]

    # Create a response dictionary
    response = {
        'result': verse_list
    }

    # Serialize the response to JSON
    json_response = json.dumps(response, ensure_ascii=False).encode('utf8').decode('utf8')

    # Return the JSON response
    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}

