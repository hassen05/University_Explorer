import streamlit as st
import pymongo
from PIL import Image
import os

# MongoDB Connection
@st.cache_resource
def get_database():
    """Connect to MongoDB and return the database object."""
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    return client["university_data"]

@st.cache_data
def load_universities():
    """Load university data from MongoDB."""
    db = get_database()
    collection = db["universities"]
    return collection.find_one()

# Custom CSS for enhanced styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f4f8;
    }
    .university-card {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit App
st.title("🎓 University Explorer")
st.markdown("*Discover Universities, Faculties, and Degrees*")

# Add a tab interface
tab1, tab2, tab3 = st.tabs(["Universities", "AI Assistant", "Search"])

with tab1:
    # Load university data from MongoDB
    data = load_universities()

    # University Selection
    st.header("Universities")
    cols = st.columns(3)

    for idx, (key, university) in enumerate(data.items()):
        if key.isdigit():  # Skip if the key is not a university entry (e.g., '0')
            col = cols[idx % 3]

            with col:
                # Display university information
                uni_name = university.get("university_name", "Unknown University")
                image_path = university.get("image", "")

                # Load and display image
                try:
                    if os.path.exists(image_path):
                        img = Image.open(image_path)
                        st.image(img, use_container_width=True)
                    else:
                        st.write(f"Image not found: {image_path}")
                except Exception as e:
                    st.write(f"Error loading image: {e}")

                if st.button(uni_name, key=uni_name):
                    st.session_state.selected_university = university  # Store the full university document

    # Faculty and Degree Display
    if "selected_university" in st.session_state:
        selected_uni = st.session_state.selected_university

        st.header(f"{selected_uni.get('university_name', 'Unknown University')} - Faculties")
        faculties = selected_uni.get("Faculties", {})

        for faculty_name, faculty_info in faculties.items():
            if st.button(faculty_info["faculty_name"], key=faculty_name):
                st.session_state.selected_faculty = faculty_info

        if "selected_faculty" in st.session_state:
            selected_faculty = st.session_state.selected_faculty

            st.subheader(f"📚 Degrees in {selected_faculty['faculty_name']}")

            degrees = selected_faculty.get("degrees", [])
            if degrees:
                for degree in degrees:
                    st.markdown(f"✨ {degree}")
            else:
                st.write("No degrees listed for this faculty.")

with tab2:
    # Embed Chatbot iframe
    st.header("AI Assistant")
    st.components.v1.iframe(
        "https://www.chatbase.co/chatbot-iframe/5VCFQ8H4CmPuKho-f_gOX",
        height=700,
    )

with tab3:
    st.header("🔍 Search by Degree or Faculty")

    # Search Input
    search_query = st.text_input("Enter a degree name or faculty name to search:")

    if search_query:
        # Perform case-insensitive search in MongoDB
        db = get_database()
        collection = db["universities"]

        results = collection.find(
            {
                "$or": [
                    {"Faculties.faculty_name": {"$regex": search_query, "$options": "i"}},
                    {"Faculties.degrees": {"$regex": search_query, "$options": "i"}},
                ]
            }
        )

        # Display Results
        st.subheader("Search Results")
        has_results = False

        for university in results:
            has_results = True
            uni_name = university.get("university_name", "Unknown University")
            st.markdown(f"### {uni_name}")

            faculties = university.get("Faculties", {})
            for faculty_name, faculty_info in faculties.items():
                if search_query.lower() in faculty_name.lower():
                    st.markdown(f"**Faculty:** {faculty_info['faculty_name']}")

                degrees = faculty_info.get("degrees", [])
                for degree in degrees:
                    if search_query.lower() in degree.lower():
                        st.markdown(f"- **Degree:** {degree}")

        if not has_results:
            st.write("No results found for your search query.")

# Footer
st.markdown("---")
st.markdown("*Explore Your Academic Journey*")
