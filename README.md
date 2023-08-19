# Online Data Science Courses

[![Source Code](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/antonAce/data-science-courses)
[![Kaggle notebook](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white)](https://www.kaggle.com/antonkozyriev/which-ds-online-course-to-take-first)
[![Made with StreamLit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://antonace-streamlit-ds-courses-introduction-qkg9ju.streamlit.app/)

All source code for [Data Science Courses](https://www.kaggle.com/antonkozyriev/online-data-science-courses) project on Kaggle platform including webcrawlers, preprocessing pipelines and EDA notebooks.


### Context

Nowadays, online educational platforms provide a vast amount of online courses. For self-learning beginners in Data Science, sometimes it's hard to choose an online course to start. This data was collected with the intent to answer common questions when choosing a new study.


### Acknowledgements

Data was collected via web scraping from popular online platforms: [Coursera](https://www.coursera.org), [Stepik](https://stepik.org), [Udemy](https://www.udemy.com), [edX](https://www.edx.org), [Pluralsight](https://www.pluralsight.com), [Alison](https://alison.com), [FutureLearn](https://www.futurelearn.com), and [Skillshare](https://www.skillshare.com). From each platform were queried courses only related to the "Data Science" topic. The original author of the [image thumbnail](https://unsplash.com/photos/Im7lZjxeLhg) is [Ales Nesetril](https://unsplash.com/@alesnesetril).


### Inspiration

The primary intent behind collecting courses data is to discover which online platform provides the highest educational quality. Also, further analysis should reveal answers like "Does a paid course provide higher quality than a free one?" or "Which platform is the most suitable for beginners?".


## Structure

 - [Web crawlers](./crawlers)
    - [Scrapy crawlers](./crawlers/scrapy)
    - [Selenium crawlers](./crawlers/standalone)
 - [On-demand dataframe](./data)
 - [EDA notebooks](./data)
 - [Data processing pipelines](./pipeline)
 - [Test suites](./test)
 - [Common utility scripts](./util)


## Getting started

Before setting up the environment, ensure you have `Make` installed on your local machine. To install the packages required for the Streamlit dashboard, use the following command:

```bash
make min-dep
```

If you prefer a virtual environment setup, use `requirements.txt`. You can set up extra dependencies for development, testing, data collection, and processing with the command:

```bash
make all-dep
```

To run a Streamlit server, use the command:

```bash
make serve
```

