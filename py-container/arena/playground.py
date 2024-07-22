# import cProfile
# import pstats
# from io import StringIO

# def my_method():
#     # Your method implementation
#     pass

# def profile_method(method):
#     pr = cProfile.Profile()
#     pr.enable()
#     method()
#     pr.disable()

#     s = StringIO()
#     sortby = 'cumulative'
#     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#     ps.print_stats()
#     print(s.getvalue())

# profile_method(my_method)

import numpy.lib.scimath as np
import coverage

# Start the coverage measurement
cov = coverage.Coverage(
    source=[".", "numpy.lib.scimath"],
    branch=True,
    include=["*/lib/python*/site-packages/*"],
)
cov.start()

# Your dynamic execution code
result = getattr(np, 'log10')(2)
print("Result:", result)

# Stop the coverage measurement
cov.stop()
cov.save()

# Report the results
cov.report()
