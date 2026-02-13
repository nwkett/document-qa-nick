import streamlit as st
from openai import OpenAI, AuthenticationError
import sys
import chromadb
from pathlib import Path
from PyPDF2 import PdfReader

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        pdf_reader = PdfReader(pdf_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        # Clean up text (remove extra whitespace)
        text = " ".join(text.split())
        return text
    except Exception as e:
        st.error(f"Error reading {pdf_path}: {str(e)}")
        return None


def add_to_collection(collection, text, file_name):
    """Add a document to the ChromaDB collection with OpenAI embeddings"""
    try:

        client = st.session_state.openai_client
        

        response = client.embeddings.create(
            input=text,
            model='text-embedding-3-small'
        )
        

        embedding = response.data[0].embedding
        
        collection.add(
            documents=[text],
            ids=[file_name],
            embeddings=[embedding]
        )
        return True
    except Exception as e:
        st.error(f"Error adding {file_name} to collection: {str(e)}")
        return False


def load_pdfs_to_collection(folder_path, collection):
    """Load all PDFs from folder into the collection"""

    if collection.count() == 0:
        pdf_files = list(Path(folder_path).glob("*.pdf"))
        
        if not pdf_files:
            st.warning(f"No PDF files found in {folder_path}")
            return False
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, pdf_path in enumerate(pdf_files):
            status_text.text(f"Loading {pdf_path.name}...")
            
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_path)
            
            if text:
                # Add to collection
                add_to_collection(collection, text, pdf_path.name)
            
            # Update progress
            progress_bar.progress((idx + 1) / len(pdf_files))
        
        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Successfully loaded {len(pdf_files)} PDF files into ChromaDB")
        return True
    else:
        st.info(f"Collection already contains {collection.count()} documents")
        return True



if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if 'Lab4_VectorDB' not in st.session_state:
    with st.spinner("Initializing ChromaDB and loading PDFs..."):
        chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab')
        collection = chroma_client.get_or_create_collection('Lab4Collection')
    

        load_pdfs_to_collection('./Lab-04-Data/', collection)
        
        st.session_state.Lab4_VectorDB = collection


def apply_buffer():
    MAX_HISTORY = 4  

    msgs = st.session_state.messages
    system_msg = msgs[:1]
    rest = msgs[1:]    

    if len(rest) > MAX_HISTORY:
        rest = rest[-MAX_HISTORY:]

    st.session_state.messages = system_msg + rest



st.title('Lab 4')

# Sidebar
openAI_model = st.sidebar.selectbox("Select Model", ('mini', 'regular'))

if openAI_model == 'mini':
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = 'gpt-4o'

#### QUERYING A COLLECTION -- ONLY USED FOR TESTING ####
# Comment this out after testing and implement your chatbot below

topic = st.sidebar.text_input('Topic', placeholder='Type your topic (e.g., GenAI)...')

if topic:
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=topic,
        model='text-embedding-3-small'
    )
    

    query_embedding = response.data[0].embedding
    
    collection = st.session_state.Lab4_VectorDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3  
    )
    

    st.subheader(f'Results for: {topic}')
    
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        
        st.write(f'**{i+1}. {doc_id}**')
        
else:
    st.info('Enter a topic in the sidebar to search the collection')


#### IMPLEMENT YOUR CHATBOT HERE (Part B) ####
