import cProfile
import io
import pstats

from pysource_codegen._codegen import generate_ast

pr = cProfile.Profile()
pr.enable()
for i in range(40):
    generate_ast(i)
pr.disable()

s = io.StringIO()
pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(30)
print(s.getvalue())
