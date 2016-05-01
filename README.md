# Package-Qualifiers

Scripts to fetch and transform data related to academic data.

# Examples

## Fetching data

### Fetch citation counts

Here's a command for fetching citations counts for papers specified in `queries.json`.
In the file, specify each query with two keys: `year` and `title`.
The `title` key can be a prefix of the actual title and should be all lower case.

    python data.py fetch citation_counts queries.json microsoft-config.json

The `microsoft-config.json` key will contain a single object with one key: `apiKey`.
This is your API key for using the [Microsoft Academic API](https://www.microsoft.com/cognitive-services://www.microsoft.com/cognitive-services/).

Data will be fetched into a SQLite `fetcher.db` by default.
Though you can also save to a Postgres database:

    python data.py fetch citation_counts queries.json --db postgres 

This command will assume that you have a `postgres-config.json` file in the local directory.
This can specify the username, password, and host for logging into the `fetcher` database.
If you want to store this config file elsewhere, you can specify the location of the file:

    python data.py fetch citation_counts queries.json --db postgres --db-config postgres-config.json

## Running migrations

If the models have been updated since you created your tables, you should run migrations on your database:

    python data.py migrate run_migration 0001_add_index_tag_excerpt_post_id

Where the last argument (`0001_add_index_tag_excerpt_post_id` in this case) is the name of the migration you want to run.
To see the available migrations, call `python data.py migrate run_migration --help`).

If you update the models, please write a migration that others can apply to their database.
See instructions in the sections below.

## Dumping data

It might be necessary to dump data to file.
You can dump special data types to file, for example:

    python data.py dump publications

This produces a file `data/dump.publications-<timestamp>.json` in CSV format.
Other dump scripts will produce data in other formats (including text and JSON).
Run `python data.py dump -h` to see what types of data can already be dumped.
And be patient---especially when these files have to do a digest of millions of rows of a table, these scripts may take a while.

You are welcome to write your own data dumping routines.
See the "Contributing" section.

# Configuring the database

You can specify the type of database and database configuration for any fetching command.
See the options in the examples for fetching queries.

# Contributing

## Writing and running tests

There is currently a small number of tests covering a portion of commands.
As you develop, anything that's functionally more complex than an iterator should ideally have a unit test.
Tests should be written and saved in the `tests` directory.

You can check that the tests pass with this command:

    python data.py tests

## Structure of a fetching module

A module for fetching or importing a specific type of data should have, at the least:
* A `configure_parser` method that takes in a subcommand parser for, and sets the command description and arguments.
* A `main` method that has the signature `main(<expected args>, *args, **kwargs)` where `<expected args>` are the arguments that you added in the `configure_parser` method

New modules should be added to the appropriate `SUBMODULES` lists at the top of the `data.py` file.
The `main` method of a fetching module can optionally be wrapped with the `lock_method(<filename>)` decorator, which enforces that the main method is only invoked once at a time.

## Writing a migration

If you update a model, it's a necessary courtesy to others to write a migration script that will apply to existing databases to bring them up to date.

Migrations are easy to write.
First, create a Python module in the `migrate` directory.
Its file name should start with a four-digit index after the index of the last-written migration (e.g., `0007` if the last migration started with `0006`).

Then, write the forward migration procedure.
You do this by instantiating a single method called `forward`, that takes a `migrator` as its only argument.
Call Peewee `migrate` methods on this object to transform the database.
For a list of available migration methods, see the [Peewee docs](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations).
This should only take a few lines of code.

We're only supporting forward migrations for now.

## Writing a data dump module

To add a script for dumping a certain type of data, decorate the `main` function of your module with `dump_json` from the `dump` module.
This decorator takes one argument: the basename of a file to save in the `data/` directory.
The `main` should do some queries to the database, and `yield` lists of records that will be saved as JSON.

## Logging messages

Every file you write should include this line after the imports and before any logic:

    logger = logging.getLogger('data')

All logging should be performed through `logger`, instead of using the `logging` module directly.
Sticking to this convention lets us configure logging globally without touching any other loggers.
