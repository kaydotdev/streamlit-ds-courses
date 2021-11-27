import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import pandas as pd


dataframe = pd.read_csv("data/dataframe.csv", index_col=0)

st.set_page_config(
   page_title="[EDA] Online Data Science Courses",
   page_icon=":notebook_with_decorative_cover:", layout="centered", initial_sidebar_state="expanded"
)

contents_selectbox = st.sidebar.selectbox(
    "Table of Contents",
    ("Introduction", "Which platforms suitable for the level",
     "What depends on the course rating", "Conclusions")
)

dashboard_description = """
[![Source Code](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/antonAce/data-science-courses)
[![Kaggle notebook](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white)](https://www.kaggle.com/antonkozyriev/which-ds-online-course-to-take-first)
[![Made with StreamLit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)]()

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

dashboard_techstack = """
Webcrawlers

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=Selenium&logoColor=white)
![Zyte](https://img.shields.io/badge/Zyte-E10098?style=for-the-badge&logoColor=white)
![Scrapy+Splash](https://img.shields.io/badge/Scrapy+Splash-60a839?&style=for-the-badge&logoColor=white)

Processing pipelines

![Conda](https://img.shields.io/badge/conda-342B029.svg?&style=for-the-badge&logo=anaconda&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626.svg?&style=for-the-badge&logo=Jupyter&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-FFFFFF?style=for-the-badge&logo=apachespark&logoColor=#E35A16)

Dashboard

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

"""


def count_values_for_feature(df: pd.DataFrame, feature_name: str):
    df_feature = df[feature_name].value_counts().to_frame()
    df_feature.reset_index(inplace=True)
    df_feature = df_feature.sort_values(feature_name, ascending=False)

    return df_feature


if contents_selectbox == "Introduction":
    st.title("Which DS online course to take first?")
    st.markdown(dashboard_description)

    st.subheader("Data preview")
    st.markdown("Structure of the collected data.")

    if st.checkbox("Display head only", value=True):
        st.dataframe(dataframe.head())
    else:
        st.dataframe(dataframe)

    st.subheader("Missing values")
    st.markdown("""
        Some insights on how many records available per each column. Platforms with *small set* of courses 
        usually **do not provide** additional information about course, like: enrolled students count, lectures durations, e.t.c.
    """)

    valid_columns = dataframe.count().to_frame(name="valid_records")

    valid_columns = valid_columns.sort_values("valid_records")
    valid_columns.reset_index(inplace=True)
    valid_columns = valid_columns.rename(columns={
        "index": "Column",
        "valid_records": "Valid records count"
    })
    fig = px.bar(valid_columns, x="Valid records count", y="Column", color="Column",
                 color_discrete_sequence=px.colors.diverging.Spectral, orientation="h")

    st.plotly_chart(fig, use_container_width=True)

elif contents_selectbox == "Which platforms suitable for the level":
    st.title("Which platform is more suitable for a specific level?")

    st.markdown("""
        The Data Science field is not a **"buzzword"** anymore, nevertheless there are still cases when people switch jobs to become Data Scientists. 
        So it's reasonable to assume that majority of the courses is dedicated to the Beginners, which is true according to the difficulty level distribution of the data.
    """)
    df_feature_level = count_values_for_feature(dataframe, "level")
    fig_level = px.pie(df_feature_level, values='level', names='index', hole=.3, color_discrete_sequence=px.colors.diverging.Spectral)
    fig_level.update_layout(title_text="Most common difficulty level")
    st.plotly_chart(fig_level, use_container_width=True)

    st.markdown("""
        Overviewed educational platforms are the most popular among existing on the Internet. Here is shown which platforms provide more content than others.
    """)
    platforms_to_group = st.multiselect('Merge the smallest platforms into a general group',
        ["Stepik", "Alison", "FutureLearn", "Pluralsight", "edX"],
        ["Stepik", "Alison", "FutureLearn", "Pluralsight"])

    dataframe_quantitative = dataframe.replace(to_replace=platforms_to_group, value='Other')

    df_feature_platform = count_values_for_feature(dataframe_quantitative, "platform")
    fig_platform = px.pie(df_feature_platform, values='platform', names='index', hole=.3, color_discrete_sequence=px.colors.diverging.Spectral)
    fig_platform.update_layout(title_text="Amount of content of educational platforms")
    st.plotly_chart(fig_platform, use_container_width=True)

    st.markdown("""
        Third-party commercial organizations publish most of the courses (like IBM, DeepLearning.AI, e.t.c.), so, as expected, the more significant part of the courses is paid.
    """)

    df_feature_free = count_values_for_feature(dataframe, "free")
    df_feature_free = df_feature_free.replace({True: "Free", False: "Paid"})
    fig_free = px.pie(df_feature_free, values='free', names='index', hole=.3, color_discrete_sequence=px.colors.diverging.Spectral)
    fig_free.update_layout(title_text="Free/Paid courses ratio")
    st.plotly_chart(fig_free, use_container_width=True)

elif contents_selectbox == "What depends on the course rating":
    st.title("What depends on the course rating?")

elif contents_selectbox == "Conclusions":
    st.title("Conclusions")

    st.subheader("EDA Insights")
    st.markdown(dashboard_insights)

    st.subheader("Techstack")
    st.markdown(dashboard_techstack)
