import os

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st
from sklearn.preprocessing import LabelEncoder

st.set_page_config(
    page_title="What depends on the course rating?",
    page_icon="⭐",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("What depends on the course rating?")

###
st.markdown(
    """
    The rating metric may give some insights into the quality of the provided learning material in the course, although it doesn't guarantee an exact quality.
    Platforms with high content variety tend to record it, so it is missing on Alison and edX. The expected rating is the highest on the Coursera platform, from 4 to 5 stars (without including outliers) and the average value.
    _So for students, who seek **paid quality content**, Coursera is the best choice._
"""
)

dataframe = pd.read_csv(st.secrets.dataframe.path, index_col=0)
corrected_rating = dataframe[(dataframe.rating > 0.0) & (dataframe.rating is not None)]
dataframe_platforms = corrected_rating["platform"].unique()
fig = go.Figure()

for platform, color in zip(
    dataframe_platforms, px.colors.diverging.Spectral[: len(dataframe_platforms)],
    strict=True
):
    fig.add_trace(
        go.Box(
            y=corrected_rating[corrected_rating.platform == platform]["rating"],
            fillcolor=color,
            marker={"size": 2, "color": "rgb(0, 0, 0)"},
            name=platform,
            line={"width": 1},
        )
    )

st.plotly_chart(fig, use_container_width=True)

###
st.markdown(
    """
    To make the course grab the student's attention, distributors have to develop relevant titles for the preview. 
    Courses may not meet the user's expectations if they cover topics inappropriate for Data Science, like coding interviews or web development. 
    Indeed, courses with a low rating tend to contain off-topic keywords in the title, like "Tetris", "JS", "Web" e.t.c. 
    And courses with the highest rating include more appropriate keywords, like "Python", "Machine learning", "Statistics" e.t.c.
"""
)

wordcloud_folder_path = os.path.join(st.secrets.assets.path, "wordcloud")
wordcloud_files = sorted(
    [
        f
        for f in os.listdir(wordcloud_folder_path)
        if os.path.isfile(os.path.join(wordcloud_folder_path, f))
    ]
)

cols = st.columns(len(wordcloud_files))

for i, row in enumerate(zip(cols, wordcloud_files, strict=True)):
    col, file = row

    with col:
        st.image(
            os.path.join(wordcloud_folder_path, file),
            use_column_width=True,
            caption=f"{i+1}-star keywords",
        )

###
st.markdown(
    """
    Remember that platforms are only responsible for distributing the courses, while their creation depends entirely on third-party organizations'. 
    Among the technical organizations with the highest rating, there are SAS, DeepLearning.AI, and IBM. 
    Meanwhile, educational institutes with the highest rating are The University of Michigan, University of California, Johns Hopkins University.
"""
)

top_distributors_count = 20
dataframe_rating = dataframe[
    (dataframe.rating > 0.0) & (dataframe.rating is not None)
].copy()

dataframe_top_distributors = (
    dataframe_rating[["author", "title"]]
    .groupby("author")
    .count()
    .sort_values(by=["title"], ascending=[False])
    .iloc[:top_distributors_count]
)

top_distributors = dataframe_top_distributors.index.values

dataframe_top_distributors_rating = (
    dataframe_rating[dataframe_rating["author"].isin(top_distributors)]
    .groupby("author")
    .agg(
        mean=pd.NamedAgg(column="rating", aggfunc="mean"),
        std=pd.NamedAgg(column="rating", aggfunc="std"),
    )
    .sort_values(by=["mean"], ascending=[True])
)

dataframe_top_distributors_rating.reset_index(inplace=True)
fig = px.bar(
    dataframe_top_distributors_rating,
    x="mean",
    y="author",
    error_x="std",
    labels={"author": "Course publisher", "mean": "Average rating"},
    color_discrete_sequence=px.colors.diverging.Spectral,
    orientation="h",
)
fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)

###
st.markdown(
    """
    Distributional platform and title relevance may influence the course rating, but they are probably not the only metrics that affect the user experience. 
    These are the following candidates that may also contribute to the course rating with the assumptions:
- **Active enrolled students** - the higher students amount, the more trust in the course from the community;
- **Level** - courses with general level may fall into a specific level category;
- **Duration** - courses with a longer timespan may cover topics not related to the user expectations;
- **Is the course free?** - if the course has a cost, it may be developed by commercial organizations with a professional approach, resulting in higher quality.
"""
)

dataframe_corr = dataframe_rating[
    ["rating", "students_count", "level", "duration", "free"]
].copy()

encoder = LabelEncoder()

dataframe_corr["level"] = encoder.fit_transform(dataframe_corr["level"].values)
dataframe_corr["free"] = encoder.fit_transform(dataframe_corr["free"].values)

fig = px.imshow(
    dataframe_corr.corr(),
    zmin=-1.0,
    zmax=1.0,
    color_continuous_scale=px.colors.sequential.Hot,
    labels={"x": "Feature", "y": "Comparison feature", "color": "Correlation value"},
)
st.plotly_chart(fig, use_container_width=True)

###
st.markdown(
    """
    Free/paid and rating are the only metrics with a high enough correlation value to be somehow related. 
    Their moderate negative correlation means that free courses tend to get a lower rating, while paid courses get a higher rating. 
    From the general cases we know, that **correlation is not causation**. Still, the assumption above explains this moderate relation well. 
    The probability estimation with the "kernel density" below supports this assumption (the most probable paid course rating is around 4.5, while free - approximately 3.0).
"""
)
group_labels = dataframe_rating["free"].unique()
hist_data = [
    dataframe_rating[dataframe_rating.free == label]["rating"].values
    for label in group_labels
]

show_hist, show_curve, show_rug = False, True, True
col_hist_option, col_rug_option = st.columns(2)

with col_hist_option:
    show_hist = st.checkbox("Show histogram", value=False)

with col_rug_option:
    show_rug = st.checkbox("Show distribution rug", value=True)

fig = ff.create_distplot(
    hist_data,
    ["Paid", "Free"],
    bin_size=0.1,
    show_hist=show_hist,
    show_curve=show_curve,
    show_rug=show_rug,
    colors=["rgb(50,136,189)", "rgb(94,79,162)"],
)

st.plotly_chart(fig, use_container_width=True)

