import sqlite3
import tempfile
import shutil
import configparser
import os
import logging

class FirefoxHistory():
    def __init__(self):
        #   Aggregate results
        self.aggregate = None
        #   Results order
        self.order = None
        #   Results number
        self.limit = None
        #   Set history location
        history_location = self.searchPlaces()
        #   Temporary  file
        #   Using FF63 the DB was locked for exclusive use of FF
        #   TODO:   Regular updates of the temporary file
        temporary_history_location = tempfile.mktemp()
        shutil.copyfile(history_location, temporary_history_location)
        #   Open Firefox history database
        self.conn = sqlite3.connect(temporary_history_location)
        #   External functions
        self.conn.create_function('hostname',1,self.__getHostname)

    def searchPlaces(self):
        #   Firefox folder path
        firefox_path = os.path.join(os.environ['HOME'], '.mozilla/firefox/')
        if os.path.exists(firefox_path) is False:
            firefox_path = os.path.join(os.environ['HOME'], 'snap/firefox/common/.mozilla/firefox/')
        #   Firefox profiles configuration file path
        conf_path = os.path.join(firefox_path,'profiles.ini')

        # Debug
        logging.debug("Config path %s" % conf_path)
        if not os.path.exists(conf_path):
            logging.error("Firefox profiles.ini not found")
            return None

        #   Profile config parse
        profile = configparser.RawConfigParser()
        profile.read(conf_path)
        prof_path = profile.get("Profile0", "Path")

        #   Sqlite db directory path
        sql_path = os.path.join(firefox_path,prof_path)
        sql_path = os.path.join(sql_path,'places.sqlite')

        # Debug
        logging.debug("Sql path %s" % sql_path)
        if not os.path.exists(sql_path):
            logging.error("Firefox places.sqlite not found")
            return None

        return sql_path


    #   Get hostname from url
    def __getHostname(self,str):
        url = str.split('/')
        if len(url)>2:
            return url[2]
        else:
            return 'Unknown'

    def search(self,query_str):
        #   Aggregate URLs by hostname
        if self.aggregate == "true":
            query = 'SELECT hostname(url)'
        else:
            query = 'SELECT DISTINCT url'
        query += ',title FROM moz_places WHERE'
        #   Search terms
        terms = query_str.split(' ')
        for term in terms:
            query += ' ((url LIKE "%%%s%%") OR (title LIKE "%%%s%%")) AND' % (term,term)
        #   Delete last AND
        query = query[:-4]

        if self.aggregate == "true":
            query += ' GROUP BY hostname(url) ORDER BY '
            #   Firefox Frecency
            if self.order == 'frecency':
                query += 'sum(frecency)'
            #   Visit Count
            elif self.order == 'visit':
                query += 'sum(visit_count)'
            #   Last Visit
            elif self.order == 'recent':
                query += 'max(last_visit_date)'
            #   Not sorted
            else:
                query += 'hostname(url)'
        else:
            query += ' ORDER BY '
            #   Firefox Frecency
            if self.order == 'frecency':
                query += 'frecency'
            #   Visit Count
            elif self.order == 'visit':
                query += 'visit_count'
            #   Last Visit
            elif self.order == 'recent':
                query += 'last_visit_date'
            #   Not sorted
            else:
                query += 'url'

        query += ' DESC LIMIT %d' % self.limit

        #   Query execution
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except Exception as e:
            logging.error("Error in query (%s) execution: %s" % (query, e))
            return None
        return rows

    def close(self):
        self.conn.close()
