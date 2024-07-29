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

import test_data_file as tdf

cls = getattr(tdf, "Test")
method = getattr(cls, "square")
method(4)
