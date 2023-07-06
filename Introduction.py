import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Streamlit dashboard: Which DS online course to take first?",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)


st.title("Which DS online course to take first?")

st.markdown(
    """
[![Source Code](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/antonAce/data-science-courses)
[![Kaggle notebook](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white)](https://www.kaggle.com/antonkozyriev/which-ds-online-course-to-take-first)

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
)

st.subheader("Data preview")
st.markdown("Structure of the collected data.")

dataframe = pd.read_csv(st.secrets.dataframe.path, index_col=0)

if st.checkbox("Display head only", value=True):
    st.dataframe(dataframe.head())
else:
    st.dataframe(dataframe)

st.subheader("Missing values")
st.markdown(
    """
    Some insights on how many records available per each column. Platforms with *small set* of courses 
    usually **do not provide** additional information about course, like: enrolled students count, lectures durations, e.t.c.
"""
)

valid_columns = (
    dataframe.count().to_frame(name="valid_records").sort_values("valid_records")
)
valid_columns.reset_index(inplace=True)
valid_columns = valid_columns.rename(
    columns={"index": "Column", "valid_records": "Valid records count"}
)

fig = px.bar(
    valid_columns,
    x="Valid records count",
    y="Column",
    color="Column",
    color_discrete_sequence=px.colors.diverging.Spectral,
    orientation="h",
)
fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)

