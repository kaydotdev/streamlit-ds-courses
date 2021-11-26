import streamlit as st
from PIL import Image


st.set_page_config(
   page_title="[EDA] Online Data Science Courses",
   page_icon=":notebook_with_decorative_cover:", layout="wide", initial_sidebar_state="expanded"
)

add_selectbox = st.sidebar.selectbox(
    "Table of Contents",
    ("Introduction", "Which platforms suitable for the level",
     "What depends on the course rating", "Insights")
)

dashboard_description = """
*[Image by Nick Morrison from unsplash.com](https://unsplash.com/photos/FHnnjk1Yj7Y)*

### Context

Nowadays, online educational platforms provide a vast amount of online courses. 
For self-learning beginners in Data Science, sometimes it's hard to choose an online lecture to start. 
This EDA intends to answer common questions when choosing a new study like **"Does a paid course provide higher quality than a free one?"** or **"Which platform is the most suitable for beginners?"**, 
and also to discover which online platform provides the highest educational quality.

### Acknowledgements

Data was collected via web scraping from popular online platforms: 
[Coursera](https://www.coursera.org), [Stepik](https://stepik.org), 
[Udemy](https://www.udemy.com), [edX](https://www.edx.org), 
[Pluralsight](https://www.pluralsight.com), [Alison](https://alison.com), 
[FutureLearn](https://www.futurelearn.com), and [Skillshare](https://www.skillshare.com). 
From each platform were queried courses only related to the "Data Science" topic.

"""

if add_selectbox == "Introduction":
    image = Image.open("static/nick-morrison.jpg")
    st.title("Which DS online course to take first?")

    st.image(image)
    st.markdown(dashboard_description)

elif add_selectbox == "Which platforms suitable for the level":
    st.title("Which platform is more suitable for a specific level?")

elif add_selectbox == "What depends on the course rating":
    st.title("What depends on the course rating?")

elif add_selectbox == "Insights":
    st.title("EDA Insights")
