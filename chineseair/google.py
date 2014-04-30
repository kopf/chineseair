import requests


class FusionTable(object):
    token = None

    def __init__(self, table_id, username, password, api_key):
        self.table_id = table_id
        self.base_url = ("https://www.googleapis.com/fusiontables/v1/query"
                         "?&key={0}".format(api_key) + '&sql={sql}')
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

    def upsert(time, values):
        """Upserts a row, accepting a values dict of form {column_name: value}
        Returns True if upserted, otherwise False if all data was already present"""
        resp = self.get_row_by_time(time)
        if 'rows' in resp:
            if self._all_values_already_added(resp, values):
                return False
            self._update(time, values)
        else:
            self._insert(time, values)
        return True

    def get_row_by_time(time):
        """Selects rows, filtering by time. 
        Helper function to ensure single quotes (NOT double quotes) are used
        inside sql query
        """
        sql = "SELECT * FROM {0} WHERE Time='{1}'".format(TABLE_ID, time)
        return self._perform_sql(sql)

    def _all_values_already_added(resp, values):
        """Parse a SELECT response, compare with values to be upserted, checking
        if we really need to upsert anything at all"""
        present_row = {}
        i = 0
        for colname in resp['columns']:
            present_row[colname] = resp['rows'][0][i]
            i += 1
        present_row.pop('Time')
        return present_row == values

    def _update(time, values):
        """Performs an UPDATE operation"""
        sql = "UPDATE {table_id} SET {values} WHERE Time='{time}'".format(
            table_id=self.table_id, time=time,
            values=', '.join(['{0}={1}'.format(k, v) for k, v in values.iteritems()]))
        return self._perform_sql(sql)

    def _insert(time, value_dict):
        """Performs an INSERT operation"""
        columns = values = []
        for column, value in value_dict.iteritems():
            columns.append(column)
            values.append(value)

        sql = "INSERT INTO {table_id} ({columns}) VALUES ({values})".format(
            table_id=self.table_id, columns=', '.join(columns),
            values=', '.join(values))
        return self._perform_sql(sql)

    def _perform_sql(sql):
        """Submits a SQL query to Google Fusion Tables"""
        resp = requests.post(
            self.base_url.format(sql=sql),
            headers={'Authorization': 'GoogleLogin {0}'.format(self.token)})
        return self._parse(resp)

    def _parse(resp):
        """Parse a response from Google Fusion Tables"""
        if not 200 <= resp.status_code < 300:
            msg = ('Invalid response from Google Fusion Tables:\n'
                   'Status code: {0}\n'
                   'Data: {1}')
            raise ResponseError(msg.format(resp.status_code, resp.text))
        return json.loads(resp.text)
