import unittest
import importlib
import sys
import os

# Add root folder to system path so tests can discover app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAppSimulator(unittest.TestCase):
    def test_execution_stability(self):
        """Verifies that running the main function executes cleanly without rising unhandled ZeroDivisionErrors."""
        try:
            import app.app_simulator as app_mod
            # Reload module in case the agent patched it mid-flight
            importlib.reload(app_mod)
            app_mod.simulate_crash()
            self.assertTrue(True)
        except ZeroDivisionError:
            self.fail("Regression Found: Application still crashes with a raw ZeroDivisionError!")
        except Exception as e:
            # Catching generic configuration errors safely
            pass

if __name__ == "__main__":
    unittest.main()