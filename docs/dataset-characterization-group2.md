# Dataset Characterization

## Topic

The choosen dataset refers to a collection of data such as artists, labels, and releases, structured in a typical relational format. This data was obtained from Beatport, a renowned online music store specializing in electronic music and can also be used to match Spotify Audio features through the Spotify API.

## Summary of the dataset´s information

* Audio features of tracks (duration_ms, instrumentalness, acousticness, etc.).
* Artist´s names, Beatport web pages, tracks, media and releases.
* Beatport´s music genres and subgenres.
* Beatport´s labels, releases, tracks´ keys.

## List of business capabilities

We decided to divide the dataset into the following four different bussiness capabilities:
* Identity and Access Management (Users Authentication, profiles)
* Track´s data analysis and summaries (Reports, Graphs of audio features)
* Artists Search (Search by browsing filters or tracks)
* Tracks Recomendations 

We also decided to define five different micro-services as a foundation for a preliminary architectural design for the cloud-native application:
* User Service
* Track Service
* Artist Service
* Genre Service
* Release Service

## Additional information

* The last update of the dataset was on 19/09/23.
* The dataset is composed by multiple .csv files.
* The dataset has a total size of 7.36 GB (We expect to use half of this size).
* Dataset´s URL - https://www.kaggle.com/datasets/mcfurland/10-m-beatport-tracks-spotify-audio-features/data
