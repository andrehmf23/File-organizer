# LibrarySet

Projeto Python organizado para gerenciar funcionalidades e testes de forma modular.

---

## Estruturação

### `utils/`
Esta pasta contém **funções e classes auxiliares** que podem ser reutilizadas em várias partes do projeto.  
Exemplos de conteúdo:
- `helper.py` → funções gerais de apoio  
- `math_ops.py` → funções matemáticas reutilizáveis  

**Como usar:**  
```python
from utils.helper import minha_funcao
minha_funcao()
```

### `tests/`
Esta pasta contém **funções e classes auxiliares** que executam testes sobre os módulos do projeto e seu sistema.
Exemplos de conteúdo:
- `test_core.py`
- `test_utils.py`

### `scripts/`
Esta pasta contém **funções e classes auxiliares** que executam tarefas externas ou processos auxiliares, que não fazem parte do código principal do pacote.

LibrarySet/
├── venv/           ← ambiente virtual
├── main.py         ← script principal
├── utils/          ← funções e classes auxiliares
├── tests/          ← testes automatizados
└── scripts/        ← scripts auxiliares executáveis
