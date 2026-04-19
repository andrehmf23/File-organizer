# -----------------------------------------
#                [Teste]
# -----------------------------------------

import os
import shutil

def recreate_folder(path):
    """
    Deleta a pasta especificada (se existir) e a recria vazia.
    """
    try:
        # Remove a pasta se existir
        if os.path.exists(path):
            shutil.rmtree(path)  # Remove pasta e todo o conteúdo
            print(f"Pasta '{path}' removida com sucesso.")

        # Cria a pasta novamente
        os.makedirs(path, exist_ok=True)
        print(f"Pasta '{path}' criada com sucesso.")

    except PermissionError:
        print(f"Erro: Permissão negada para modificar '{path}'.")
    except OSError as e:
        print(f"Erro ao manipular a pasta '{path}': {e}")

# -----------------------------------------


from utils.fileOrganizer import *

recreate_folder("./test")

start = time.perf_counter()

org = FileOrganizer(
    target=r"/home/andre/Músicas",
    destination=r"./test",
    level_limit=10,
    copy=True,
    organizer=Organizer.ALPHABETICAL,
    date_tree=True,
    data_order="dmy"
)

print("A: " + org.detect_script(c))
print("a: " + org.detect_script("arrow"))
print("ç: " + org.detect_script("caça"))
print("部: " + org.detect_script("部"))


"""

end = time.perf_counter()
print(f"Tempo de criação: {end - start:.6f} segundos")

start = time.perf_counter()

org.collect()

end = time.perf_counter()
print(f"Tempo de execução: {end - start:.6f} segundos")

"""