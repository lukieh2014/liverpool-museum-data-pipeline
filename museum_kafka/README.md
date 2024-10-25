WELCOME, WELCOME, Please take a seat..

You will see a script, consumer.py, in the corner of your eye, says I. My oh my, I hear you cry, what a wonderful script, like chicken pie!

Okay enough, onto the details:

Consumer.py is a masterful creation. It takes in a live data stream from Kafka (kiosk exhibition ratings and requests from the Liverpool Museum of Natural History), and processes that data real-time before adding it to a remote RDS. It even sets up the empty tables in that remote database if required. It is worth noting that it does not create the RDS instance, this must be done first using the terraform script 'main.tf'.

Before using this script, some set-up is required. First, activate a .venv and install the requirements found in requirements.txt.
Then, set the right TOPIC at the top of consumer.py for the incoming data stream.
Next, change the variables inside '.env' as follows:

BOOTSTRAP_SERVERS=
SECURITY_PROTOCOL=
SASL_MECHANISM=         These all relate to connecting to the Kafka data stream.
KUSERNAME=
KPASSWORD=

aws_access_key_id=
aws_secret_access_key=
region=
DB_NAME2=                 These all relate to connecting to the RDS instance.
PASSWORD=
HOST=
USERNAME=

There are currently 2 command-line arguments that can be used:

- '-l' : can specify the location to log any errors in invalid messages that come through the data stream. Must be 'term' (to log to terminal, default) or 'file' (to log to the file 'logged_errors.txt').
- '-s' : if this is your first time connecting to the RDS, you will need to set up the empty tables for the data to be inputted into. This argument takes either 'true' or 'false' (defaults to false). If you enter 'true', it will run the file 'schema.sql' and set up the empty database. NOTE: SELECTING THIS OPTION WILL DELETE ANY EXISTING DATA IN THE DATABASE !!

Your script should now be ready to run!

(note - if messages aren't coming through, try changing the 'group.id' in the config (around line 170) to a different number.)
(note - 'auto.offset.reset' in config (see above note) is set to 'latest' to take in the latest messages added to the stream. This can be changed to 'earliest' to take in historical data from the stream.)

