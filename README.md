# FakeNewsDetection
Milestones for Data Science course 2020 at UCPH

MILESTONE with DEADLINE 24th APRIL DESCRIPTION

Now that we have covered basic database and data exploration skills, it's time to start thinking about the project. Since the project spans over a long period, we have placed a milestone midway in the project, just to check that everyone is roughly on track. The milestone takes the form of a short jupyter notebook, which must be handed in on Friday, April 24 (midnight). The milestone will be assessed as pass/non-pass, and passing the milestone is a requirement for attending the exam. Note that you should hand in this milestone as a group.



The milestone will focus on the database and data processing parts of the pipeline: e.g. getting data, cleaning data, exploring data, putting it in a database etc. Your expected to solve the following tasks:



Task 1

If you haven't already done so, the first task is to form a group of 2-3 people. Go to the Absalon course page and create a group called "Project group X”, where X is a number (please fill up the group names by increasing index, so we don't have any gaps). Make sure that you list the names of all members of the group at the top of the jupyter notebook along with your group number.



Task 2

The second task is to demonstrate that you have a working database containing the FakeNewsCorpus dataset. Explain your choice of schema design. You have been working on this task on a small subset of the data during the TA-sessions. For this milestone, demonstrate that your database contains a larger number of rows (e.g. one million - or however many you can reasonably work with on your available hardware), and that it supports simple queries.



Task 3

Once your database is loaded, you can start issuing queries to better understand the characteristics of the data. Formulate the following queries in the database languages requested (in the square brackets following each item) and briefly discuss what you observe when you execute them over your database: 



List the domains of news articles of reliable type and scrapped at or after January 15, 2018. NOTE: Do not include duplicate domains in your answer. [Languages: relational algebra and SQL]
List the name(s) of the most prolific author(s) of news articles of fake type. An author is among the most prolific if it has authored as many or more fake news articles as any other author in the dataset. [Languages: extended relational algebra and SQL]
Count the pairs of article IDs that exhibit the exact same set of meta-keywords, but only return the pairs where the set of meta-keywords is not empty. [Language: SQL]


Task 4

Now try to explore the FakeNewsCorpus dataset. Make at least three non-trivial observations/discoveries about the data. These observations could be related to outliers, artefacts, or even better: genuinely interesting patterns in the data that could potentially be used for fake-news detection. Examples of simple observations could be how many missing values there are in particular columns - or what the distribution over domains is. Be creative! :). Note that many of these observations can be extracted as direct queries to the database, for instance using GROUP BY and COUNT.



Task 5

In this task you should create your very own news data set by scraping it from the web. We will be looking at the "Politics and Conflict" section of the Wikinews site (https://en.wikinews.org/wiki/Category:Politics_and_conflicts), which contains about 7500 articles sorted by the first letter in their title. Since we want the different groups to have slightly different experiences with this data, each group should try to extract the articles for a specific range of letters - given by the python expression:

"ABCDEFGHIJKLMNOPRSTUVWZABCDEFGHIJKLMNOPRSTUVWZ"[group_nr%23:group_nr%23+10]

where group_nr is your group number (according to Task 1). The data set you produce should contain fields corresponding to the content of the article, in addition to some metadata fields like the date when the article was written. Describe the tools you used, and any challenges that you faced, and report some basic statistics on the data (e.g. number of rows, fields, etc). Note that there are no fake/no-fake labels in this dataset - we will consider it as a trusted source of only true articles (which is perhaps a bit naive).



Task 6

You will hand-in your jupyter notebook by submitting it to the peergrade system. Please make sure that you submit it as a group and specify all group members within the peergrade system.



Task 7

Each group will be asked to evaluate the work of three other groups, based on a short list of criteria that you can find within the peergrade system. This will only work well if everyone puts some effort into providing constructive comments, so please allocate some time to do this properly. It is an opportunity to get some feedback that can help you improve your final project. The deadline for giving feedback is a week after the hand-in deadline.
