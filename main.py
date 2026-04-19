from utils.fileOrganizer import *

org = FileOrganizer(
    target=r"/home/andre/Músicas",
    destination=r"./test",
    level_limit=10,
    copy=True,
    structure="md",
)

org._destination_resolve

org.collect()
