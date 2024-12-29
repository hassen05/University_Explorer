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


# Custom CSS for Design Improvements
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fafafa; /* Soft background color */
        font-family: 'Arial', sans-serif;
    }
    .university-card {
        background-color: white;
        border-radius: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        cursor: pointer;
    }
    .university-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .university-card img {
        border-radius: 10px;
        object-fit: cover;
        max-width: 100%;
        max-height: 200px;
    }
    .search-box input {
        border-radius: 8px;
        padding: 10px;
        width: 80%;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    .search-box button {
        border-radius: 8px;
        padding: 10px 15px;
        background-color: #4CAF50;
        color: white;
        border: none;
        cursor: pointer;
        margin-left: 10px;
    }
    .search-box button:hover {
        background-color: #45a049;
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
    data = load_universities()

    st.header("Universities")

    # Create a uniform grid with 3 columns
    cols = st.columns(3, gap="large")

    image_width = 200
    image_height = 200

    for idx, (key, university) in enumerate(data.items()):
        if key.isdigit():
            col = cols[idx % 3]  # Use modulus to loop through columns

            with col:
                # Set up consistent padding and layout
                uni_name = university.get("university_name", "Unknown University")
                image_path = university.get("image", "")

                # Display the image with fixed size
                try:
                    if os.path.exists(image_path):
                        img = Image.open(image_path)
                        img = img.resize((image_width, image_height))  # Resize to fixed dimensions
                        st.image(img, use_container_width=True)
                    else:
                        st.write(f"Image not found: {image_path}")
                except Exception as e:
                    st.write(f"Error loading image: {e}")

                # Add a button below the image with a hover effect
                if st.button(uni_name, key=f"button_{uni_name}"):
                    st.session_state.selected_university = university

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
    # AI Assistant tab with better layout
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
        data = load_universities()

        st.subheader("Search Results")
        has_results = False

        for key, university in data.items():
            if key.isdigit():
                uni_name = university.get("university_name", "Unknown University")
                faculties = university.get("Faculties", {})

                university_shown = False

                for faculty_info in faculties.values():
                    faculty_name = faculty_info.get("faculty_name", "")
                    degrees = faculty_info.get("degrees", [])

                    matching_degrees = [d for d in degrees if search_query in d.lower()]
                    faculty_matches = search_query in faculty_name.lower()

                    if faculty_matches or matching_degrees:
                        has_results = True

                        if not university_shown:
                            st.markdown(f"### {uni_name}")
                            university_shown = True

                        st.markdown(f"**Faculty:** {faculty_name}")

                        if matching_degrees:
                            for degree in matching_degrees:
                                st.markdown(f"- **Degree:** {degree}")

        if not has_results:
            st.write("No results found for your search query.")

# Footer
st.markdown("---")
st.markdown("*Explore Your Academic Journey*")
