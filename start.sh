# start psql database
# pg_ctl start -l logfile -D /home/jlab/github/test-beam-2023-unpacker/database/test_data_location

# start app with N workers
gunicorn app:server -b:8123 --workers 8