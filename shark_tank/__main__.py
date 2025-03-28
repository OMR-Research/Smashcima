import unittest
import os

# Execute with:
# .venv/bin/python3 -m shark_tank

# NOTE: Shark tank are tests that do not test a specific feature,
# instead they test overall stability. The goal is to throw as much
# real-world data samples at various components of Smashcima and make
# it does not crash.

suite = unittest.TestLoader().discover(
    start_dir=os.path.dirname(__file__),
    top_level_dir=os.path.join(os.path.dirname(__file__), "../"),
    pattern="*Test.py"
)
unittest.TextTestRunner(verbosity=2).run(suite)
