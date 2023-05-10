import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app_settings import DATAFRAME_PATH


def group_feature_val(df: pd.DataFrame, name: str):
    df = df[name].value_counts().to_frame()
    df.reset_index(inplace=True)
    df = df.sort_values(name, ascending=False)

    return df


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

dataframe = pd.read_csv(DATAFRAME_PATH, index_col=0)
df_feature_level = group_feature_val(dataframe, "level")

fig_level = px.pie(
    df_feature_level,
    values="level",
    names="index",
    hole=0.3,
    color_discrete_sequence=px.colors.diverging.Spectral,
)
st.plotly_chart(fig_level, use_container_width=True)

st.markdown(
    """
    Overviewed educational platforms are the most popular among existing on the Internet. Here is shown which platforms provide more content than others.
"""
)
platforms_to_group = st.multiselect(
    "Merge the smallest platforms into a general group",
    ["Stepik", "Alison", "FutureLearn", "Pluralsight", "edX"],
    ["Stepik", "Alison", "FutureLearn", "Pluralsight"],
)

dataframe_quantitative = dataframe.replace(to_replace=platforms_to_group, value="Other")
df_feature_platform = group_feature_val(dataframe_quantitative, "platform")
fig_platform = px.pie(
    df_feature_platform,
    values="platform",
    names="index",
    hole=0.3,
    color_discrete_sequence=px.colors.diverging.Spectral,
)
st.plotly_chart(fig_platform, use_container_width=True)

st.markdown(
    """
    Third-party commercial organizations publish most of the courses (like IBM, DeepLearning.AI, e.t.c.), so, as expected, the more significant part of the courses is paid.
"""
)

df_feature_free = group_feature_val(dataframe, "free")
df_feature_free = df_feature_free.replace({True: "Free", False: "Paid"})
fig_free = px.pie(
    df_feature_free,
    values="free",
    names="index",
    hole=0.3,
    color_discrete_sequence=px.colors.diverging.Spectral,
)
st.plotly_chart(fig_free, use_container_width=True)

st.markdown(
    f"""
    The **Beginner** level is the level of most courses, dedicated for students who only started their Data Science journey or for learners who want to try themselves in another field of activity. 
    **Udemy** platform offers the greatest amount of courses for **Beginner** and **General** levels, which are the most suitable levels for the learners' group mentioned above. 
    For more experienced learners, **Coursera** is a better choice in terms of content variety for **Intermediate** and **Advanced** levels.
"""
)

dataframe_difficulty = (
    dataframe.groupby(["platform", "level"]).size().reset_index(name="counts")
)
dataframe_levels = dataframe_difficulty["level"].unique()

fig = go.Figure(
    data=[
        go.Bar(
            name=level,
            marker_color=color,
            x=dataframe_difficulty[dataframe_difficulty.level == level]["platform"],
            y=dataframe_difficulty[dataframe_difficulty.level == level]["counts"],
        )
        for level, color in zip(
            dataframe_levels, px.colors.diverging.Spectral_r[: len(dataframe_levels)]
        )
    ]
)

fig.update_layout(barmode="group")
st.plotly_chart(fig, use_container_width=True)
