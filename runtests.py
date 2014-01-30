import unittest
import macropy.activate
from macropy.core.exporters import SaveExporter
macropy.exporter = SaveExporter("exported", ".")

import test.testAST
import test.testJeevesConfidentiality
import test.testSourceTransform
import test.testZ3
import test.gallery.battleship.testBattleship

unittest.TextTestRunner().run(unittest.TestSuite([
    unittest.defaultTestLoader.loadTestsFromModule(test.testAST),
    unittest.defaultTestLoader.loadTestsFromModule(test.testJeevesConfidentiality),
    unittest.defaultTestLoader.loadTestsFromModule(test.testZ3),
    unittest.defaultTestLoader.loadTestsFromModule(test.testSourceTransform),
    unittest.defaultTestLoader.loadTestsFromModule(test.gallery.battleship.testBattleship),
]))
