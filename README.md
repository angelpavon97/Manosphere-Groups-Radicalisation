# TFM - Manosphere groups radicalisation

This repository contains the scripts used as well as the results obtained from the master's thesis: Text analytic approaches for analysing information sharing in radicalised manosphere communities. Thus, the aim of this project will be to analyse the information shared in manosphere communities to see what type of information is most shared, which generates the most debate and the topics and relationships inherent in these discussions.

The structure of this repository is as follows:


- **images**: Folder containing the images extracted from the data. Its subfolders are the following:
  - **graphs**: Charts showing the most posted urls in the comments, the most posted urls in the initial posts and the most discussed urls by the manosphere communities.
  - **word_clouds**: Folder containing the word clouds of comments discussing the most relevant urls from the manosphere communities.
- **topic_modeling**: Folder containing the data and images obtained with the probabilistic topic modelling.
  - **clustering**: Contains the results of applying clustering techniques for probabilistic topic models.
      - _CRCD_: It contains the clusters obtained after applying Cumulative Ranking-based Clustering on the LDA models obtained from the comments made by users of manosphere groups on the shared links. 
      - _RCD_: It contains the clusters obtained after applying Ranking-based Clustering on the LDA models obtained from the comments made by users of manosphere groups on the shared links. 
  - **matrixes**: It contains images of matrixes that indicate the percentage of topics that make up the comments on each extracted link.
  - **models**: Contains trained LDA models on the comments of the links using as parameters different numbers of topics and iterations.
  - **text_razor**: Contains the topics extracted by a categorisation tool (TextRazor).
  - **topics**: Contains files summarising the data obtained from the trained LDA models. Thus, each file has the same name as the trained models in the _models_ folder and contains the topics obtained as well as the topics assigned to each link.
- ***IncelsSQL.py***: It contains the IncelsSQL class, a class used to create and manage the different tables of the database to facilitate the extraction of the results.
- ***main.py***: Main program used to create tables from the data base and obtain the graphs showing the most relevant information.
- ***text_razor.py***: Script that uses the TextRazor tool to categorise urls according to their comments.
- ***topic_modeling.py***: Script that applies topic modelling as well as the use of these models to obtain the matrixes and apply the clustering techniques mentioned above.

Documentation: https://www.overleaf.com/read/nrxfhtwxgrpk
