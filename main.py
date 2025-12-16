from utils.fileOrganizer import *

org = FileOrganizer(
    target=r"",
    destination=r"",
    level_limit=10,
    organizer=Organizer.DATE,
    date_tree=True,
    date_preset="ym"
)

org.collect()
