import functools
import os
import sqlparse
import time

from django.db import connection


def format_elapsed_time(elapsed_time):
    """
    From time duration float, format in hours, minutes, seconds

    Args:
        elapsed_time (float): Time duration

    Returns:
        str: Formated time
    """
    hours, minutes = map(int, [elapsed_time // 3600, (elapsed_time % 3600) // 60])
    seconds = elapsed_time % 60
    return f'{hours}h:{minutes}m:{seconds:.3f}s'

############################################################################################
########### DEBUGGER DECORATOR FOR DEV PURPOSES. COMMENT OUT FOR COVERAGE REPORT ###########
############################################################################################

# def function_debugger(_func=None, *, show_queries=False, tofile=False):
#     """
#     Decorator factory supporting
#     - kwargs in decorator usage
#     - usage with or without ()
#     Use like:
#     - @function_debugger, or @function_debugger() or
#     - @function_debugger(show_queries=True/False)
#     """
#     DEBUG_LOG_FILE = os.path.join(os.getcwd(), 'debug_output.log')

#     def log(msg, append=True):
#         print(msg)
#         if tofile:
#             mode = 'a' if append else 'w'
#             with open(DEBUG_LOG_FILE, mode, encoding='utf-8') as f:
#                 f.write(str(msg) + '\n')

#     def decorator(func):
#         """
#         Decorator to monitor
#         - Queries made to the database
#         - Total time
#         from a function
#         """
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             log('\n'.join([100 * '=', f" Debugging: `{func.__name__}` ".center(100, '='), 100 * '=']), append=False)
#             initial_queries_cnt = len(connection.queries)
#             start = time.time()
#             result = func(*args, **kwargs)
#             duration = time.time() - start
#             current_queries_cnt = len(connection.queries)
#             queries_from_func_cnt = current_queries_cnt - initial_queries_cnt
#             if show_queries:
#                 modify_query = lambda k,v: sqlparse.format(v, reindent_aligned=True) if k == 'sql' else v  # noqa: E731
#                 queries_from_func = connection.queries[initial_queries_cnt:]
#                 queries_from_func = [{k:modify_query(k, v) for k, v in q.items()} for q in queries_from_func]
#                 log(' DB queries: '.center(50, '='))
#                 for i, v in enumerate(queries_from_func, 1):
#                     log(f"[{i}]: ")
#                     log(v['sql'])
#                     log(f"Time: {v['time']}s")
#             log(f'===> DB queries count: {queries_from_func_cnt}')
#             log(f'===> Total Time: {duration:.5f}s')
#             return result
#         return wrapper
#     return decorator if _func is None else decorator(_func)
