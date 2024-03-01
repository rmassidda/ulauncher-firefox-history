import configparser
import logging
import os
import shutil
import sqlite3
import tempfile


class FirefoxHistory:
    def __init__(self):
        #   Aggregate results
        self.aggregate = None
        #   Results order
        self.order = None
        #   Results number
        self.limit = None
        #   Set history location
        places_path = self.searchPlaces()
        #   Check if the history file exists
        if places_path is None:
            logging.error("History file does not exist (%s)", places_path)
            raise FileNotFoundError
        #   Temporary file
        #   Using FF63 the DB was locked for exclusive use of FF
        #   TODO:   Regular updates of the temporary file
        temporary_history_location = tempfile.mktemp()
        shutil.copyfile(places_path, temporary_history_location)
        #   Open Firefox history database
        self.conn = sqlite3.connect(temporary_history_location)
        #   External functions
        self.conn.create_function("hostname", 1, self.__getHostname)

    def searchPlaces(self):
        """
        Get the path to the Firefox places.sqlite file
        """
        logging.debug("Trying to find the Firefox history file")
        home = os.environ["HOME"]
        # Try default path
        possible_paths = {
            "home": os.path.join(home, ".mozilla/firefox/"),
            "snap": os.path.join(
                home, "snap/firefox/common/.mozilla/firefox/"
            ),
            "flatpak": os.path.join(
                home, ".var/app/org.mozilla.firefox/.mozilla/firefox/"
            ),
        }

        firefox_path = None
        for key, path in possible_paths.items():
            if os.path.exists(path):
                logging.debug("Found Firefox user directory: %s", key)
                firefox_path = path
                break

        if firefox_path is None:
            logging.error("Could not find the Firefox user directory.")
            return None

        # Firefox profiles configuration file path
        conf_path = os.path.join(firefox_path, "profiles.ini")
        profile = configparser.RawConfigParser()

        try:
            profile.read(conf_path)
            prof_path = profile.get("Profile0", "Path")
        except Exception as e:
            logging.error("Error reading Firefox profile: %s", e)
            return None

        # Sqlite db directory path
        places_path = os.path.join(firefox_path, prof_path)
        places_path = os.path.join(places_path, "places.sqlite")

        return places_path

    #   Get hostname from url
    def __getHostname(self, string):
        url = string.split("/")
        if len(url) > 2:
            return url[2]
        else:
            return "Unknown"

    def search(self, query_str):
        #   Aggregate URLs by hostname
        if self.aggregate == "true":
            query = "SELECT hostname(url)"
        else:
            query = "SELECT DISTINCT url"
        query += ",title FROM moz_places WHERE"
        #   Search terms
        terms = query_str.split(" ")
        for term in terms:
            query += ' ((url LIKE "%%%s%%") OR (title LIKE "%%%s%%")) AND' % (
                term,
                term,
            )
        #   Delete last AND
        query = query[:-4]

        if self.aggregate == "true":
            query += " GROUP BY hostname(url) ORDER BY "
            #   Firefox Frecency
            if self.order == "frecency":
                query += "sum(frecency)"
            #   Visit Count
            elif self.order == "visit":
                query += "sum(visit_count)"
            #   Last Visit
            elif self.order == "recent":
                query += "max(last_visit_date)"
            #   Not sorted
            else:
                query += "hostname(url)"
        else:
            query += " ORDER BY "
            #   Firefox Frecency
            if self.order == "frecency":
                query += "frecency"
            #   Visit Count
            elif self.order == "visit":
                query += "visit_count"
            #   Last Visit
            elif self.order == "recent":
                query += "last_visit_date"
            #   Not sorted
            else:
                query += "url"

        query += " DESC LIMIT %d" % self.limit

        #   Query execution
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def close(self):
        self.conn.close()
