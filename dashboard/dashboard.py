import streamlit as st
import pandas as pd


dataframe = pd.read_csv("data/dataframe.csv", index_col=0)

st.set_page_config(
   page_title="[EDA] Online Data Science Courses",
   page_icon=":notebook_with_decorative_cover:", layout="centered", initial_sidebar_state="expanded"
)

add_selectbox = st.sidebar.selectbox(
    "Table of Contents",
    ("Introduction", "Which platforms suitable for the level",
     "What depends on the course rating", "Insights")
)

dashboard_description = """
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

dashboard_insights = """
 1. The majority of the Data Science courses are dedicated to Beginners;
 2. The most common keywords in Data Science courses are: `Python`, `Machine learning`, `Data`, `R`, `Deep Learning`, `Statistics`, `TensorFlow` e.t.c.;
 3. `Udemy` is the most suitable platform for Beginners and General level students, and `Coursera` - for Intermediate and Expert;
 4. Among platforms with the most significant amount of content, `Coursera` has the highest average rating;
 5. Top tech organizations that have the highest average rating are `SAS`, `DeepLearning.AI`, `IBM`, and top educational organizations are `The University of Michigan`, `University of California`, `Johns Hopkins University`;
 6. The rating of the course may indeed depend on whether it is free or not;
"""

if add_selectbox == "Introduction":
    st.title("Which DS online course to take first?")
    st.markdown(dashboard_description)

    st.subheader("Data preview")
    st.markdown("Structure of the collected data.")

    if st.checkbox('Display only head', value=True):
        st.dataframe(dataframe.head())
    else:
        st.dataframe(dataframe)

elif add_selectbox == "Which platforms suitable for the level":
    st.title("Which platform is more suitable for a specific level?")

elif add_selectbox == "What depends on the course rating":
    st.title("What depends on the course rating?")

elif add_selectbox == "Insights":
    st.title("EDA Insights")
    st.markdown(dashboard_insights)
