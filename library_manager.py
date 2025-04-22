import streamlit as st
import pandas as pd
import json
import os
# import osfroom datatime import datetime
import time
#import random
#simport plotly.express as px
#import plotly.graph_objects as go
#import streamlit_lottie import st_lottie  
import requests

# set page config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

#custom CSS for the styling
st.markdown(
    """
    <style>
            .main-header {
                font-size: 3rem !important;
                color: #1E3A8A;
                font-weight: 700;
                margin-bottom: 1rem;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }
            .sub-header {
                font-size: 1.8rem !important;
                color: #3B82F6;
                font-weight: 600;
                margin-top: 1rem;
                margin-bottom: 1rem;
                
            }
            
            .success-message {
                padding: 1rem;
                background-color: #ECDF5;
                border-left: 5px solid #10B981;
                border-radius: 0.375rem;
            }
            
            .warning-message {
                padding: 1rem;
                background-color: #FEF3C7;
                border-left: 5px solid #EF4444;
                border-radius: 0.375rem;
            }  
            
            .book-card {
                background-color: #F9FAFB;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left: 5px solid #3B82F6;
                transition: transform 0.3s ease;
            }  
            
            .book-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
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
            .action-button {
                margin-right: 0.5rem;
            }
            .stButton>button {
                border-radius: 0.375rem;
            }
                            
                
    </style>
    """,
    unsafe_allow_html=True,
)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except: 
        return None
    
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
    
#load library   
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
            return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False
    
#save library
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False
    
#add book to library
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
    st.session_state.book_added = True
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5) #animation delay
    
#remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

#search book
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = []
    
    for book in st.session_state.library:
        if search_by == "title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results
    
##calculate library statistics
def calculate_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    
    genres = {}
    authors = {}
    decades = {}
    
    for book in st.session_state.library:
        if book["genre"] in genres:
            genres[book["genre"]] += 1
        else:
            genres[book["genre"]] = 1
     
 #count authors
        if book["author"] in authors:
            authors[book["author"]] += 1
        else:
            authors[book["author"]] = 1
        
    #count decades
    decade = (book["publication_year"] // 10) * 10
    if decades in decades:
        decades[decades] += 1
    else:
        decades[decades] = 1
        
#short by count
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))    
    
    return {
        "total_books": total_books,
        "read_books": read_books,
        "percentage_read": percentage_read,
        "genres": genres,
        "authors": authors,
        "decades": decades
    }
    
def create_visulations(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats["read_books"], stats["total_books"] - stats["read_books"]],
            hole=0.4,
            marker_colors=["#10B981", "#EF4444"]
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
    #bar chart for genres
    if stats['genres']:
        genres_df = pd.DataFrame({
            "Genre": list(stats["genres"].keys()),
            "Count": list(stats["genres"].values())
        })
        fig_genres = px.bar(
            genres_df,
            x="Genre",
            y="Count", 
            color="Count",
           color_continous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(
            title_text="Books by publication decade",
            xaxis_title="Decade",
            yaxis_title="Numbers of books",
            height=400
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='splinea'
        )
        fig_decades.update_layout(
            title_text="Books by publication decade",
            xaxis_title="Decade",
            yaxis_title="Numbers of books",
            height=400
        )
        st.plotly_chart(fig_decades, use_container_width=True)
        
#load library
load_library()
st.sidebar.markdown("<h1 style='text-align: center;'> Navigation </h1>", unsafe_allow_html=True)   
lottie_book = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_4j8v2g5h.json")
if lottie_book:
    with st.sidebar:
        st.sidebar_lottie(lottie_book, height=200, key="book_animation")
        
nav_options = st.sidebar.radio(
    "choose an option",
    ["View Library", "Add Book", "Search Book", "Library Statistics"])

#change current view based on navigation

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_options == "Search Book":
    st.session_state.current_view = "search_book"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "library_statistics"
    
st.markdown("<h1 class='main-header'>Personal Library Management System</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>View Library</h2>", unsafe_allow_html=True)
    
#adding books input form
    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2023)
            
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction",
                "Non-Fiction",
                "Science Fiction",
                "Fantasy",
                "Mystery",
                "Biography",
                "History",
                "Romance",
                "Thriller",
                "Self-Help",
                "Science",
                "Poetry",
                "Graphic Novel",
                "Children's",
                "Young Adult",
                "Cookbook",
                "Travel",
                "Health",
                "Religion",
                "Philosophy",
                "Business",
                "Technology",
                "Comics",
                "Classic",
                "Other",
                
                
                
                
            ]) 
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        submit_button = st.form_submit_button(label="Add Book")   
        
        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_bool)
    
    if st.session_state.book_added:
        st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False
    elif st.session.current_view == "library":
      st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)     
      
      if not st.session_state.library:
          st.markdown("<div class 'warning-message'>Your library is empty. Please add books to your library.</div>", unsafe_allow_html=True)
      else:
          cols = st.columns(2)
          for i , book in enumerate(st.session_state.library):
              with cols[i % 2]:
                  st.markdown(f"""<div class='book-card'>
                              <h3>{book['title']}</h3>
                              <p><strong>Author:</strong> {book['author']}</p>
                               <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                                <p><strong>Genre:</strong> {book['genre']}</p>
                                <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{
                                    "Read" if book["read_status"] else "Unread"
                                }</span></p>
                                </div>
""", unsafe_allow_html=True)
                  
          col1, col2 = st.columns(2)
          with col1:
                    if st.button(f"Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                           st.retrun()
          with col2:
              new_status = not book['read_status']
              status_label = "Mark as read" if not book['read_status'] else "Mark as unread"
              if st.button(status_label, key=f"status_{i}", use_container_width=True):
                 st.session_state.library[i]['read_status'] = new_status
                 save_library()
                 st.rerurn()
    if st.session_state.book_removed:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False
       
elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search Book</h2>", unsafe_allow_html=True)
    
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"]) 
    search_term = st.text_input("Enter search term:")
    
    if st.button("Search", use_container_width=False):  
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
            search_book(search_term, search_by)  
    if hasattr(st.session_state, 'search_results'):
        if st.session_state.search_results: 
            st.markdown(f"<h3> Found {len(st.session_state.search_results)} results:</h3>", unsafe_allow_html=True)
            
            for i, book in enumerate(st.session_state.search_results):
                st.markdown(f"""<div class='book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                             <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                              <p><strong>Genre:</strong> {book['genre']}</p>
                              <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{
                                  "Read" if book["read_status"] else "Unread"
                              }</span></p>
                              </div>
""", unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>No results found matching your search.</div>", unsafe_allow_html=True)    
            
elif st.session_state.current_view =="stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to see stats!</div>", unsafe_allow_html=True)   
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats["total_books"])
        with col2:
            st.metric("Read Books", stats["read_books"])  
        with col3:
            st.metric("Percentage Read", f"{stats['percentage_read']:.2f}%")
        create_visulations()  
        
        if stats["author"]:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = list(stats["authors"].keys())[:5]
            for author, count in stats["authors"].items():
                st.markdown(f"** {author}**: {count} book{'s' if count > 1 else 'book'}")
st.markdown("---")         
st.markdown("Copyright © 2023 Saima Khan Personal Library Manager", unsafe_allow_html=True)       
                           
                                   
                             
                              
                  
   
   
        
            
           
        
           
          
            
          
        
