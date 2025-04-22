import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import requests
#import plotly.express as px
import plotly.graph_objects as go

# set page config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #3B82F6;
        font-weight: 600;
        margin-top: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #D1FAE5;
        border-left: 5px solid #10B981;
        border-radius: 0.375rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        border-radius: 0.375rem;
    }
    .book-card {
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
    }
    .read-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badge {
        background-color: #EF4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
    except Exception as e:
        st.error(f"Error loading library: {e}")

def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
    except Exception as e:
        st.error(f"Error saving library: {e}")

def add_book(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by.lower() == "title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by.lower() == "author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by.lower() == "genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

def calculate_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres, authors, decades = {}, {}, {}
    for book in st.session_state.library:
        genres[book["genre"]] = genres.get(book["genre"], 0) + 1
        authors[book["author"]] = authors.get(book["author"], 0) + 1
        decade = (book["publication_year"] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percentage_read": percentage_read,
        "genres": dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        "authors": dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        "decades": dict(sorted(decades.items(), key=lambda x: x[0]))
    }

def create_visualizations(stats):
    if stats['total_books'] > 0:
        fig_read = go.Figure(data=[go.Pie(labels=["Read", "Unread"], values=[stats['read_books'], stats['total_books'] - stats['read_books']], hole=0.4)])
        st.plotly_chart(fig_read, use_container_width=True)

    if stats['genres']:
        df = pd.DataFrame({"Genre": list(stats["genres"].keys()), "Count": list(stats["genres"].values())})
        fig = px.bar(df, x="Genre", y="Count", color="Count", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    if stats['decades']:
        df = pd.DataFrame({"Decade": [f"{d}s" for d in stats['decades']], "Count": list(stats['decades'].values())})
        fig = px.line(df, x="Decade", y="Count", markers=True)
        st.plotly_chart(fig, use_container_width=True)

# Load data and UI
load_library()

st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to", ["View Library", "Add Book", "Search Book", "Library Statistics"])

st.session_state.current_view = nav.replace(" ", "_").lower()

st.markdown("<h1 class='main-header'>Personal Library Management System</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "view_library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty.</div>", unsafe_allow_html=True)
    else:
        for i, book in enumerate(st.session_state.library):
            st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <span class='{"read-badge" if book['read_status'] else "unread-badge"}'>
                        {"Read" if book['read_status'] else "Unread"}
                    </span>
                </div>
            """, unsafe_allow_html=True)

elif st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Year", min_value=1000, max_value=datetime.now().year, value=2023)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Mystery", "Romance", "Other"])
        status = st.radio("Read Status", ["Read", "Unread"])
        submitted = st.form_submit_button("Add Book")
        if submitted:
            add_book(title, author, year, genre, status == "Read")
            st.success("Book added successfully!")

elif st.session_state.current_view == "search_book":
    st.markdown("<h2 class='sub-header'>Search Book</h2>", unsafe_allow_html=True)
    by = st.selectbox("Search By", ["Title", "Author", "Genre"])
    term = st.text_input("Search term")
    if st.button("Search"):
        search_book(term, by)
        for book in st.session_state.search_results:
            st.markdown(f"<div class='book-card'><h3>{book['title']}</h3><p><strong>Author:</strong> {book['author']}</p></div>", unsafe_allow_html=True)

elif st.session_state.current_view == "library_statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>No books in library.</div>", unsafe_allow_html=True)
    else:
        stats = calculate_stats()
        st.metric("Total Books", stats['total_books'])
        st.metric("Read Books", stats['read_books'])
        st.metric("% Read", f"{stats['percentage_read']:.2f}%")
        create_visualizations(stats)

st.markdown("---")
st.markdown("Copyright © 2023 Saima Khan Personal Library Manager")

