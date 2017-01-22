class QueryHelper:

    def __init__(self, driver):
        self._driver = driver
        self.session = self._driver.session()

    def stopSession(self):
        self.session.close()

    def runQuery(self, query, mapping):
        result = []

        for record in self.session.run(query, mapping):
            result.append(record)

        # Returns [None] if db doesnt return a result
        # Need to check if this ever happens, as it requires handling when calling the func
        # Temp fix: Wrap None in a list...
        return [None] if not result else result