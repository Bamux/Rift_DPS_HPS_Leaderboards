# Rift DPS HPS Leaderboards

Python scripts, MySQL Database and templates with which the leaderboards are created.

Example Website: http://rift-stats.s3-website.eu-central-1.amazonaws.com

## Installation Instructions:
1. Import the database.mysql from the database folder into your database.
2. Configure the mysql_connect_config.py in the scripts folder to connect to your database
3. Start the main.py in the scripts folder. The script reads the data from https://prancingturtle.com/, enters it into your database and generates html files in the public folder. It is also possible to automate the upload of html files to a web server.
