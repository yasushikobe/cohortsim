import unittest

from Database import Database


class TestDatabase(unittest.TestCase):

    def testCreateDatabase(self):
        PATIENTCOUNT = 1000
        OBSERVATIONYEARS = 10
        INCIDENCE = 0.010
        database = self.__createDatabase(INCIDENCE, PATIENTCOUNT, OBSERVATIONYEARS)
        self.assertEqual(database.incidence, INCIDENCE)
        self.assertEqual(database.observationYears, OBSERVATIONYEARS)
        self.assertEqual(database.patientCount, PATIENTCOUNT)
        self.assertEqual(database.data.shape, (PATIENTCOUNT, OBSERVATIONYEARS))

    def testElectCohort(self):
        PATIENTCOUNT = 1000
        OBSERVATIONYEARS = 10
        INCIDENCE = 0.010
        ELECTPATIENTCOUNT = 100
        database = self.__createDatabase(INCIDENCE, PATIENTCOUNT, OBSERVATIONYEARS)
        cohort = database.electCohort(ELECTPATIENTCOUNT)
        self.assertEqual(cohort.incidence, INCIDENCE)
        self.assertEqual(cohort.observationYears, OBSERVATIONYEARS)
        self.assertEqual(cohort.patientCount, ELECTPATIENTCOUNT)
        self.assertEqual(cohort.data.shape, (ELECTPATIENTCOUNT, OBSERVATIONYEARS))

    def __createDatabase(self, incidence, patientCount, observationYears) -> 'Database':
        return Database(incidence, patientCount, observationYears)
