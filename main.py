from utils.fileOrganizer import *
import time

org = FileOrganizer(
    target=r"/home/andre/Downloads/",
    destination=r"./test",
    level_limit=10,
    copy=True,
    structure="md",
    show=True
)

start = time.perf_counter()

org.collect()
                      
end = time.perf_counter()
print(f"Collect dssokdjsodhnislevou {end - start:.4f}s")
