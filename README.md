# Database installation and config notes

## psycopg2
For installing psycopg2 pg_config should be in the path
Therefore before running `poetry update` or similar commands just run the following in the terminal
PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"

## Database and user
The default user for postgres should be postgres with same password as username
Also psql CLI would have been installed when install postgres.app
The following set of commands would be required

```
psql postgres

create role sdas createdb login password 'sdas';
create database artmind_config with owner = sdas;
create database artmind_data with owner = sdas;
```

To see the listing of databases and roles from the psql postgres command line `\l` and `\du` commands respectively can be used