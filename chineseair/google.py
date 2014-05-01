import itertools
import json
import time

import logbook
import requests


COLUMNS = ['Time', 'Beijing', 'Shanghai', 'Chengdu', 'Guangzhou']
log = logbook.Logger()

class ConnectionError(Exception):
    pass


class ResponseError(Exception):
    pass

class RateLimitExceeded(Exception):
    pass


def split_list(iterable, n):
    """Split list into groups of n items: http://stackoverflow.com/a/1625013/221001"""
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.izip_longest(*args))


class FusionTable(object):
    token = None

    def __init__(self, table_id, username, password, api_key):
        log.info('Connecting to table {0}'.format(table_id))
        self.table_id = table_id
        self.base_url = ("https://www.googleapis.com/fusiontables/v1/query"
                         "?&key={0}".format(api_key))
        resp = requests.post(
            'https://www.google.com/accounts/ClientLogin',
            headers={'Content-type': 'application/x-www-form-urlencoded'},
            params={'accountType': 'GOOGLE', 'Email': username,
                    'Passwd': password, 'service': 'fusiontables',
                    'source': 'ventolin.org'})
        for segment in resp.text.split('\n'):
            if 'Auth=' in segment:
                self.token = segment.replace('Auth=', 'auth=')
                break
        if not self.token:
            raise ConnectionError('Unable to obtain Google API Token')

    def upsert(self, time, values):
        """Upserts a row, accepting a values dict of form {column_name: value}
        Returns True if upserted, otherwise False if all data was already present"""
        log.info('Upserting {0} - {1}'.format(time, values))
        resp = self.get_row_by_time(time)
        if 'rows' in resp:
            rowid = resp['rows'][0][0]
            if self._all_values_already_added(resp, values):
                return False
            self._perform_sql(self._create_update_sql(rowid, values))
        else:
            self._perform_sql(self._create_insert_sql(time, values))
        return True

    def get_row_by_time(self, time):
        """Selects rows, filtering by time. 
        Helper function to ensure single quotes (NOT double quotes) are used
        inside sql query
        """
        sql = "SELECT ROWID, {0} FROM {1} WHERE Time='{2}'".format(
            ', '.join(COLUMNS), self.table_id, time)
        return self._perform_sql(sql)

    def bulk_insert(self, values):
        """Perform a bulk INSERT of values of the form
        {'time': '1990-01-01 12:00:00', 'city': 'Beijing', 'value': '200'}
        """
        log.info('Performing a bulk insert of {0} rows'.format(len(values)))
        for group in split_list(values, 500):
            sql = ''
            for row in group:
                sql += self._create_insert_sql(
                    row['time'], {row['city']: row['value']})
            self._perform_sql(sql)
            log.info('Inserted 500 records')

    def _all_values_already_added(self, resp, values):
        """Parse a SELECT response, compare with values to be upserted, checking
        if we really need to upsert anything at all"""
        present_row = {}
        i = 0
        for colname in resp['columns']:
            present_row[colname] = resp['rows'][0][i]
            i += 1
        del present_row['Time']
        del present_row['rowid']
        return present_row == values

    def _create_update_sql(self, rowid, values):
        """Performs an UPDATE operation"""
        sql = "UPDATE {table_id} SET {values} WHERE ROWID='{rowid}'; ".format(
            table_id=self.table_id, rowid=rowid,
            values=', '.join(['{0}={1}'.format(k, v) for k, v in values.iteritems()]))
        return sql

    def _create_insert_sql(self, time, value_dict):
        """Performs an INSERT operation"""
        columns = []
        values = []
        for column, value in value_dict.iteritems():
            columns.append(column)
            values.append(value)

        sql = "INSERT INTO {table_id} (Time, {columns}) VALUES ('{time}', {values}); ".format(
            table_id=self.table_id, columns=', '.join(columns),
            values=', '.join(values), time=time)
        return sql

    def _perform_sql(self, sql):
        """Submits a SQL query to Google Fusion Tables"""
        resp = requests.post(
            self.base_url,
            headers={'Authorization': 'GoogleLogin {0}'.format(self.token)},
            data={'sql': sql})
        try:
            retval = self._parse(resp)
        except RateLimitExceeded:
            log.error('Rate limit exceeded. Sleeping for 20 seconds.')
            time.sleep(20)
            return self._perform_sql(sql)
        return retval

    def _parse(self, resp):
        """Parse a response from Google Fusion Tables"""
        if not 200 <= resp.status_code < 300:
            msg = (u'Invalid response from Google Fusion Tables:\n'
                   u'Status code: {0}\n'
                   u'Data: {1}')
            if resp.status_code == 403:
                raise RateLimitExceeded()
            else:
                log.error(msg.format(resp.status_code, resp.text))
                raise ResponseError()
        return json.loads(resp.text)
