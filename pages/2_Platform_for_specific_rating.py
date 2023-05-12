import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app_settings import DATAFRAME_PATH


st.set_page_config(
    page_title="Which platform is more suitable for a specific level?",
    page_icon="❓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("Which platform is more suitable for a specific level?")

st.markdown(
    """
    The Data Science field is not a **"buzzword"** anymore, nevertheless there are still cases when people switch jobs to become Data Scientists. 
    So it's reasonable to assume that majority of the courses is dedicated to the Beginners, which is true according to the difficulty level distribution of the data.
    """
)

with st.sidebar:
    st.subheader("Platforms groups")

    st.markdown(
        """
        To make feature comparison in this section more clear on the charts, we need to group platforms with low number of samples into a general category.
        """
    )

    platforms_to_group = st.multiselect(
        "Choose platforms to group into 'Other' category",
        ["Stepik", "Alison", "FutureLearn", "Pluralsight", "edX"],
        ["Stepik", "Alison", "FutureLearn", "Pluralsight"],
    )


dataframe = pd.read_csv(DATAFRAME_PATH, index_col=0)
dataframe_quantitative = dataframe.replace(to_replace=platforms_to_group, value="Other")
df_feature_groups = {}

for feature in ["level", "platform", "free"]:
    df_feature_group = dataframe_quantitative[feature].value_counts().to_frame()
    df_feature_group.reset_index(inplace=True)
    df_feature_groups[feature] = df_feature_group.sort_values(feature, ascending=False)

fig_level = px.pie(
    df_feature_groups["level"],
    values="count",
    names="level",
    hole=0.3,
    color_discrete_sequence=px.colors.diverging.Spectral,
)
st.plotly_chart(fig_level, use_container_width=True)

st.markdown(
    """
    Overviewed educational platforms are the most popular among existing on the Internet. Here is shown which platforms provide more content than others.
"""
)

fig_platform = px.pie(
    df_feature_groups["platform"],
    values="count",
    names="platform",
    hole=0.3,
    color_discrete_sequence=px.colors.diverging.Spectral,
)
st.plotly_chart(fig_platform, use_container_width=True)

st.markdown(
    """
    Third-party commercial organizations publish most of the courses (like IBM, DeepLearning.AI, e.t.c.), so, as expected, the more significant part of the courses is paid.
"""
)

fig_free = px.pie(
    df_feature_groups["free"].replace({True: "Free", False: "Paid"}),
    values="count",
    names="free",
    hole=0.3,
    color_discrete_sequence=px.colors.diverging.Spectral,
)
st.plotly_chart(fig_free, use_container_width=True)

st.markdown(
    """
    The **Beginner** level is the level of most courses, dedicated for students who only started their Data Science journey or for learners who want to try themselves in another field of activity. 
    **Udemy** platform offers the greatest amount of courses for **Beginner** and **General** levels, which are the most suitable levels for the learners' group mentioned above. 
    For more experienced learners, **Coursera** is a better choice in terms of content variety for **Intermediate** and **Advanced** levels.
"""
)

df_course_difficulty = dataframe.groupby(["platform", "level"]).size().to_frame().rename(columns={ 0: "counts" })
df_course_difficulty.reset_index(inplace=True)
dataframe_levels = df_course_difficulty["level"].unique()

fig = go.Figure(
    data=[
        go.Bar(
            name=level,
            marker_color=color,
            x=df_course_difficulty[df_course_difficulty.level == level]["platform"],
            y=df_course_difficulty[df_course_difficulty.level == level]["counts"],
        )
        for level, color in zip(
            dataframe_levels, px.colors.diverging.Spectral_r[: len(dataframe_levels)]
        )
    ]
)

fig.update_layout(barmode="group")
st.plotly_chart(fig, use_container_width=True)
