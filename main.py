from utils.fileOrganizer import *
import time

p = Path("./test").resolve()
print(p.resolve())
print(p)

org = FileOrganizer(
    target=r"/home/andre/Músicas/",
    destination=r"./test",
    level_limit=10,
    copy=True,
    structure="sa",
    show=True
)

org.aphabetical_range('A', 'Z')


start = time.perf_counter()

org.collect()
                      
end = time.perf_counter()
print(f"Collect levou {end - start:.4f}s")
