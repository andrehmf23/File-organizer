# File Organizer

Projeto em Python para organizar e separar arquivos em pastas de forma automática, com suporte a filtros e múltiplas estratégias de organização.

---

## Descrição

O File Organizer percorre uma pasta de origem de forma recursiva e organiza os arquivos em uma pasta de destino, de acordo com regras configuráveis como ordem alfabética, data ou extensão do arquivo.

---

## Parâmetros

### Parâmetros principais

target  
Pasta principal (origem dos arquivos)

destination  
Pasta de destino dos arquivos organizados

level_limit  
Profundidade máxima de pastas a serem percorridas

copy  
True para copiar os arquivos, False para mover

organizer  
Tipo de organização disponível:
- DIRECT
- ALPHABETICAL
- DATE
- SUFFIX

---

### Organização por data

date_tree  
Quando True, cria uma estrutura de pastas em árvore.  
Quando False, cria uma única pasta com a data formatada.

date_preset  
Define o formato da data utilizada na organização.  
Presets disponíveis:

- y   → ano (ex: 2025)
- ym  → ano/mês (ex: 2025/03)
- ymd → ano/mês/dia (ex: 2025/03/12)
- m   → mês (ex: 03)
- md  → mês/dia (ex: 03/12)
- d   → dia (ex: 12)

---

## Filtros

name  
Filtra por nome exato do arquivo

type  
Filtra por extensão do arquivo (sem o ponto)

date_start  
Data inicial no formato YYYY-MM-DD

date_end  
Data final no formato YYYY-MM-DD

---

## Utilização

### Exemplo básico

```python
from file_organizer import FileOrganizer, Organizer

organizer = FileOrganizer(
    target="temp",
    destination="organized",
    level_limit=10,
    organizer=Organizer.DATE,
    date_tree=True,
    date_preset="ym"
)

organizer.collect(organizer.target)
```