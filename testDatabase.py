import unittest
import pandas

from Database import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.PATIENTCOUNT = 1000
        self.OBSERVATIONYEARS = 10
        self.INCIDENCE = 0.010
        self.ELECTPATIENTCOUNT = 100
        self.database = self.__createDatabase(self.INCIDENCE, self.PATIENTCOUNT, self.OBSERVATIONYEARS)

    def testCreateDatabase(self):
        self.assertEqual(self.database.incidence, self.INCIDENCE)
        self.assertEqual(self.database.observationYears, self.OBSERVATIONYEARS)
        self.assertEqual(self.database.patientCount, self.PATIENTCOUNT)
        self.assertEqual(self.database.data.shape, (self.PATIENTCOUNT, self.OBSERVATIONYEARS))

    def testElectCohort(self):
        cohort = self.database.electCohort(self.ELECTPATIENTCOUNT)
        self.assertEqual(cohort.incidence, self.INCIDENCE)
        self.assertEqual(cohort.observationYears, self.OBSERVATIONYEARS)
        self.assertEqual(cohort.patientCount, self.ELECTPATIENTCOUNT)
        self.assertEqual(cohort.data.shape, (self.ELECTPATIENTCOUNT, self.OBSERVATIONYEARS))

    def testGetOnsetDataFrame(self):
        onsetDataFrame = self.database.getOnsetDataFrame()
        self.assertIs(type(onsetDataFrame), pandas.core.frame.DataFrame)
        self.assertEqual(onsetDataFrame.index.size, 10)

    def testGetRateTheory(self):
        rateTheory = self.database.getRateTheory()
        self.assertIs(type(rateTheory), pandas.core.frame.DataFrame)
        self.assertEqual(rateTheory.index.size, 10)

    def __createDatabase(self, incidence, patientCount, observationYears) -> 'Database':
        return Database(incidence, patientCount, observationYears)
