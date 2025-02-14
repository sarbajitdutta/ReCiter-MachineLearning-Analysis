import json
import urllib.request
import time
import os
import pymysql.cursors
import pymysql.err


def connect_mysql_server(username, db_password, db_hostname, database_name):
    """Establish a connection to MySQL or MariaDB server. This function is
    depandend on the PyMySQL library.
    See: https://github.com/PyMySQL/PyMySQL

    Args:
        username (string): username of the database user.
        password (string): password of the database user.
        db_hostname (string): hostname or IP address of the database server.
        database_name (string): the name of the database we are connecting to.

    Returns:
        MySQLConnection object.
    """

    try:
        mysql_db = pymysql.connect(user=username,
                                   password=db_password,
                                   host=db_hostname,
                                   database=database_name)

        print("Connected to database server: " + db_hostname,
                "; database: " + database_name,
                "; with user: " + username)

        return mysql_db

    except pymysql.err.MySQLError as err:
        print(time.ctime() + "--" + "Error connecting to the database. %s" % (err))


def get_personarticle_pmid(mysql_cursor):
    """Looks up a list to PMIDs from the
       reciter.personArticle table

    Args:
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.

    Returns:
        pmid (list): List of all rows in the pmid column.
    """
    get_metadata_query = (
        """
        SELECT distinct
            CAST(pmid as char) as pmid
        FROM reciter.personArticle
        WHERE userAssertion = 'ACCEPTED'
        """
    )

    mysql_cursor.execute(get_metadata_query)

    pmid = list()

    for rec in mysql_cursor:
        pmid.append(rec[0])

    return pmid


def create_nih_API_url(article_pmid_list):
    """Create RCR API URL by combining the
    base API and fields of intrest. API
    documentation can be found at:
    https://icite.od.nih.gov/api

    Multi record. This function combines
    all PMIDs from the list in one long URL.

    Args:
        article_pmid (list of PMIDs): API pmid.

    Returns:
        string: Full API URL of the record.

    Here's a sample JSON record: https://icite.od.nih.gov/api/pubs?pmids=19393196
    """

    API_BASE_URL = "https://icite.od.nih.gov/api/pubs?pmids="

    combined_pmids = ",".join(article_pmid_list)

    full_api_url = API_BASE_URL + combined_pmids

    return full_api_url


def truncate_analysis_rcr(mysql_cursor):
    """This function will delete all rows in the
    analysis_rcr table when called.

    Args:
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.
    """

    truncate_rcr_query = (
        """
        truncate analysis_rcr;
        """
    )

    mysql_cursor.execute(truncate_rcr_query)
    print(time.ctime() + "--" + "Existing analysis_rcr table truncated.")


def truncate_analysis_rcr_cites(mysql_cursor):
    """This function will delete all rows in the
    analysis_rcr_cites table when called.

    Args:
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.
    """

    truncate_rcr_query = (
        """
        truncate analysis_rcr_cites;
        """
    )

    mysql_cursor.execute(truncate_rcr_query)
    print(time.ctime() + "--" + "Existing analysis_rcr_cites table truncated.")


def truncate_analysis_rcr_cites_clin(mysql_cursor):
    """This function will delete all rows in the
    analysis_rcr_cites_clin table when called.

    Args:
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.
    """

    truncate_rcr_query = (
        """
        truncate analysis_rcr_cites_clin;
        """
    )

    mysql_cursor.execute(truncate_rcr_query)
    print(time.ctime() + "--" + "Existing analysis_rcr_cites_clin table truncated.")


def get_json_data(api_record_url):
    """Gets JSON data from API URL

    Args:
        api_record_url (string): URL of the API returning JSON data.

    Returns:
        dict: Python dictionary with JSON data or error.
    """
    try:
        api_request = urllib.request.urlopen(api_record_url)
        json_api_data = json.loads(api_request.read().decode())
        return json_api_data

    except urllib.error.URLError as err:
        print(time.ctime() + "--" + "%s--API URL: %s" % (err, api_record_url))
    except ValueError as err:
        print(time.ctime() + "--" + "Error parsing JSON data--Error %s" % (err))


def get_dict_value(dict_obj, *keys):
    """Gets the value of a key in a dictionary object.
        If the key is not found it returns None.

    Args:
        dict_obj (dict): Dictionary object to check.
        keys (string): Name of key or nested keys to search.

    Raises:
        AttributeError: If dictionary object is not passwed.

    Returns:
        Value of the key if found or None if not.
    """
    if not isinstance(dict_obj, dict):
        raise AttributeError("dict_obj needs to be of type dict.")

    dict_value = dict_obj

    for key in keys:
        try:
            dict_value = dict_value[key]
        except KeyError:
            return None
    return dict_value


def get_rcr_records(nih_api_url):
    """Gets and returns API records from the RCR URL.

    Args:
        nih_api_url (string): URL of the API record.

    Returns:
        list: RCR API record list of tuples.
    """

    rcr_record = get_json_data(nih_api_url)

    if isinstance(rcr_record, dict):
        # We map dictionary value to each table column. This should
        # allow for easy update if the database tables or API records
        # change in the future.
        #
        # Because the API does not always return data for all keys,
        # we have to check each one with the get_dict_value function
        # and assign None (NULL) for the missing values.
        process_records = get_dict_value(rcr_record, "data")

        records = []

        for record in process_records:
            new_record = (
                get_dict_value(record, "pmid"),
                get_dict_value(record, "year"),
                get_dict_value(record, "is_research_article"),
                get_dict_value(record, "is_clinical"),
                get_dict_value(record, "relative_citation_ratio"),
                get_dict_value(record, "nih_percentile"),
                get_dict_value(record, "citation_count"),
                get_dict_value(record, "citations_per_year"),
                get_dict_value(record, "expected_citations_per_year"),
                get_dict_value(record, "field_citation_rate"),
                get_dict_value(record, "provisional"),
                get_dict_value(record, "doi"),
                get_dict_value(record, "human"),
                get_dict_value(record, "animal"),
                get_dict_value(record, "molecular_cellular"),
                get_dict_value(record, "apt"),
                get_dict_value(record, "x_coord"),
                get_dict_value(record, "y_coord"),
                get_dict_value(record, "cited_by_clin"),
                get_dict_value(record, "cited_by"),
                get_dict_value(record, "references")
            )

            records.append(new_record)

        print(time.ctime() + "--" + "New records retrived--API URL: %s" % (nih_api_url))
        return records

    return "Invalid record obtained from API URL"

def insert_analysis_rcr(mysql_db, mysql_cursor, db_records):
    """Inserts the API records in the MySQL analysis_rcr database table.

    Args:
        mysql_db (MySQLConnection object): The MySQL database where the table resides.
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.
        db_records (list): List of rows to be added to the database.

    Returns:
        string: Records added successfully or error message.
    """

    add_to_rcr_table = (
        """
        INSERT INTO reciter.analysis_rcr(
           `pmid`,
           `year`,
           `is_research_article`,
           `is_clinical`,
           `relative_citation_ratio`,
           `nih_percentile`,
           `citation_count`,
           `citations_per_year`,
           `expected_citations_per_year`,
           `field_citation_rate`,
           `provisional`,
           `doi`,
           `human`,
           `animal`,
           `molecular_cellular`,
           `apt`,
           `x_coord`,
           `y_coord`
        )
        VALUES(
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        """
    )

    try:
        mysql_cursor.executemany(add_to_rcr_table, db_records)
        mysql_db.commit()

        print(time.ctime() + "--" + "%s records successfully added to the database."
            % (len(db_records)))

    except pymysql.err.MySQLError as err:
        print(time.ctime() + "--" + "Error writing the records to the database. %s" % (err))


def insert_analysis_rcr_cites(mysql_db, mysql_cursor, db_records):
    """Inserts the API records in the MySQL analysis_rcr_cites_clin database table.

    Args:
        mysql_db (MySQLConnection object): The MySQL database where the table resides.
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.
        db_records (list): List of rows to be added to the database.

    Returns:
        string: Records added successfully or error message.
    """

    add_to_rcr_table = (
        """
        INSERT INTO reciter.analysis_rcr_cites(
           `citing_pmid`,
           `cited_pmid`
        )
        VALUES(
            %s, %s
        )
        """
    )

    try:
        mysql_cursor.executemany(add_to_rcr_table, db_records)
        mysql_db.commit()

        print(time.ctime() + "--" + "%s records successfully added to the database."
            % (len(db_records)))

    except pymysql.err.MySQLError as err:
        print(time.ctime() + "--" + "Error writing the records to the database. %s" % (err))


def insert_analysis_rcr_cites_clin(mysql_db, mysql_cursor, db_records):
    """Inserts the API records in the MySQL analysis_rcr_cites_clin database table.

    Args:
        mysql_db (MySQLConnection object): The MySQL database where the table resides.
        mysql_cursor (CMySQLCursor): Executes an SQL query against the database.
        db_records (list): List of rows to be added to the database.

    Returns:
        string: Records added successfully or error message.
    """

    add_to_rcr_table = (
        """
        INSERT INTO reciter.analysis_rcr_cites_clin(
           `citing_pmid`,
           `cited_pmid`
        )
        VALUES(
            %s, %s
        )
        """
    )

    try:
        mysql_cursor.executemany(add_to_rcr_table, db_records)
        mysql_db.commit()

        print(time.ctime() + "--" + "%s records successfully added to the database."
            % (len(db_records)))

    except pymysql.err.MySQLError as err:
        print(time.ctime() + "--" + "Error writing the records to the database. %s" % (err))


if __name__ == '__main__':
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')

    # Create a MySQL connection to the Reciter database
    reciter_db = connect_mysql_server(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    reciter_db_cursor = reciter_db.cursor()

    # Truncate the analysis_rcr, analysis_rcr_cites, and analysis_rcr_cites_clin
    # tables to remove all old records.
    truncate_analysis_rcr(reciter_db_cursor)
    truncate_analysis_rcr_cites(reciter_db_cursor)
    truncate_analysis_rcr_cites_clin(reciter_db_cursor)

    # Get the PMIDs from the personArticle table
    person_article_pmid = get_personarticle_pmid(reciter_db_cursor)

    # Take 900 PMIDs at a time, create an API URL with them,
    # and get data for the records.
    # This is an API limitation of 1000 records, but 900 is
    # actually working without errors.
    analysis_rcr_rec = []
    analysis_rcr_cites_rec = []
    analysis_rcr_cites_clin = []

    for i in range(0, len(person_article_pmid), 900):
        # Create API URL
        api_url = create_nih_API_url(person_article_pmid[i:i+900])
        # Get records from API
        rcr_records = get_rcr_records(api_url)

        if rcr_records is not None:
            for item in rcr_records:
                # Get the records needed for
                # the analysis_rcr table
                analysis_rcr_rec.append(item[:18])

                # Process cited_by_clin
                if item[18] is not None:
                    for cited_by_clin_item in item[18]:
                        cited_by_clin = (cited_by_clin_item, item[0])
                        analysis_rcr_cites_clin.append(cited_by_clin)

                # Process cited_by for the analysis_rcr_cites table
                if item[19] is not None:
                    for cited_by_item in item[19]:
                        cited_by = (cited_by_item, item[0])
                        analysis_rcr_cites_rec.append(cited_by)

                # Process references for the analysis_rcr_cites table
                if item[20] is not None:
                    for references_item in item[20]:
                        references = (references_item, item[0])
                        analysis_rcr_cites_rec.append(references)

        # Instert current records to the database
        insert_analysis_rcr(reciter_db, reciter_db_cursor, analysis_rcr_rec)
        insert_analysis_rcr_cites(reciter_db, reciter_db_cursor, analysis_rcr_cites_rec)
        insert_analysis_rcr_cites_clin(reciter_db, reciter_db_cursor, analysis_rcr_cites_clin)

        # Clear the processed records from memory
        rcr_records.clear()
        analysis_rcr_rec.clear()
        analysis_rcr_cites_rec.clear()
        analysis_rcr_cites_clin.clear()
        # Pause for 1 second between API calls
        time.sleep(1)

    # Close DB connection
    reciter_db.close()
    reciter_db_cursor.close()
