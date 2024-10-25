This is a README for the import data script.

The script will search for files in the S3 bucket 'sigma-resources-museum', and download any relevant .csv or .json files.

Relevant files are files that begin with 'lmnh' i.e. Liverpool Museum of Natural History.

All csv files are then combined into one file (merged_csv.csv) before deleting the individual csv files.

Finally, the data from the merged CSV file is then imported into the database. The user can take advantage of the following (optional) command line arguments:

-b : specify the name of the bucket which contains the desired files.
-r : specify the number of rows from the merged CSV that the user would like to be imported to the DB.
-l : specify the logging output destination (file or terminal, defaults to terminal).
