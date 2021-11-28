import stylecloud

import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
import pandas as pd

from preprocessing import text_preprocessing
from static import *

from os import listdir
from os.path import isfile, join


wordcloud_folder_name = "wordcloud"
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
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

elif contents_selectbox == "Which platforms suitable for the level":
    st.title("Which platform is more suitable for a specific level?")

    st.markdown("""
        The Data Science field is not a **"buzzword"** anymore, nevertheless there are still cases when people switch jobs to become Data Scientists. 
        So it's reasonable to assume that majority of the courses is dedicated to the Beginners, which is true according to the difficulty level distribution of the data.
    """)
    df_feature_level = count_values_for_feature(dataframe, "level")
    fig_level = px.pie(df_feature_level, values='level', names='index', hole=.3, color_discrete_sequence=px.colors.diverging.Spectral)
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
    st.plotly_chart(fig_platform, use_container_width=True)

    st.markdown("""
        Third-party commercial organizations publish most of the courses (like IBM, DeepLearning.AI, e.t.c.), so, as expected, the more significant part of the courses is paid.
    """)

    df_feature_free = count_values_for_feature(dataframe, "free")
    df_feature_free = df_feature_free.replace({True: "Free", False: "Paid"})
    fig_free = px.pie(df_feature_free, values='free', names='index', hole=.3, color_discrete_sequence=px.colors.diverging.Spectral)
    st.plotly_chart(fig_free, use_container_width=True)

    st.markdown(f"""
        The **Beginner** level is the level of most courses, dedicated for students who only started their Data Science journey or for learners who want to try themselves in another field of activity. 
        **Udemy** platform offers the greatest amount of courses for **Beginner** and **General** levels, which are the most suitable levels for the learners' group mentioned above. 
        For more experienced learners, **Coursera** is a better choice in terms of content variety for **Intermediate** and **Advanced** levels.
    """)

    dataframe_difficulty = dataframe.groupby(['platform', 'level']).size().reset_index(name='counts')
    dataframe_levels = dataframe_difficulty['level'].unique()

    fig = go.Figure(data=[
        go.Bar(
            name=level,
            marker_color=color,
            x=dataframe_difficulty[dataframe_difficulty.level == level]["platform"],
            y=dataframe_difficulty[dataframe_difficulty.level == level]["counts"])
        for level, color in zip(dataframe_levels, px.colors.diverging.Spectral_r[:len(dataframe_levels)])
    ])

    fig.update_layout(barmode='group')
    st.plotly_chart(fig, use_container_width=True)

elif contents_selectbox == "What depends on the course rating":
    st.title("What depends on the course rating?")

    ###
    st.markdown("[TODO] Rating distribution over platforms.")

    corrected_rating = dataframe[(dataframe.rating > 0.0) & (dataframe.rating is not None)]
    dataframe_platforms = corrected_rating['platform'].unique()
    fig = go.Figure()

    for platform, color in zip(dataframe_platforms, px.colors.diverging.Spectral[:len(dataframe_platforms)]):
        fig.add_trace(go.Box(
            y=corrected_rating[corrected_rating.platform == platform]["rating"], 
            fillcolor=color,
            marker=dict(
                size=2,
                color='rgb(0, 0, 0)'
            ),
            line=dict(width=1)))

    st.plotly_chart(fig, use_container_width=True)

    ###
    st.markdown("[TODO] Plot keywords set for each rating category.")

    wordcloud_files = sorted([f for f in listdir(wordcloud_folder_name)
                              if isfile(join(wordcloud_folder_name, f))])

    cols = st.columns(len(wordcloud_files))

    for i, row in enumerate(zip(cols, wordcloud_files)):
        col, file = row

        with col:
            st.image(f"{wordcloud_folder_name}/{file}", use_column_width=True, caption=f"{i+1}-star keywords")

    ###
    st.markdown("[TODO] determine the average rating of the TOP-20 organization with the most significant amount of courses available.")

    top_distributors_count = 20
    dataframe_rating = dataframe[(dataframe.rating > 0.0) & (dataframe.rating is not None)].copy()

    dataframe_top_distributors = dataframe_rating[["author", "title"]].groupby("author").count().sort_values(
        by=["title"], ascending=[False]
    ).iloc[:top_distributors_count]

    top_distributors = dataframe_top_distributors.index.values

    dataframe_top_distributors_rating = dataframe_rating[
        dataframe_rating["author"].isin(top_distributors)
    ].groupby("author").agg(
        mean=pd.NamedAgg(column="rating", aggfunc="mean"),
        std=pd.NamedAgg(column="rating", aggfunc="std"),
    ).sort_values(by=["mean"], ascending=[True])

    dataframe_top_distributors_rating.reset_index(inplace=True)
    fig = px.bar(dataframe_top_distributors_rating, x="mean",
                 y="author", error_x="std",
                 labels={
                    "author": "Course publisher",
                    "mean": "Average rating"
                 },
                 color_discrete_sequence=px.colors.diverging.Spectral_r,
                 orientation="h")
    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

elif contents_selectbox == "Conclusions":
    st.title("Conclusions")

    st.subheader("EDA Insights")
    st.markdown(dashboard_insights)

    st.subheader("Techstack")
    st.markdown(dashboard_techstack)
