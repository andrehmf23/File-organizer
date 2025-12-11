# LibrarySet

Projeto Python organizado para gerenciar funcionalidades e testes de forma modular.

---

## Estrutura de Pastas

### `utils/`
Esta pasta contém **funções e classes auxiliares** que podem ser reutilizadas em várias partes do projeto.  
Exemplos de conteúdo:
- `helper.py` → funções gerais de apoio  
- `math_ops.py` → funções matemáticas reutilizáveis  

**Como usar:**  
```python
from utils.helper import minha_funcao
minha_funcao()

LibrarySet/
├── venv/           ← ambiente virtual
├── main.py         ← script principal
├── utils/          ← funções e classes auxiliares
├── tests/          ← testes automatizados
└── scripts/        ← scripts auxiliares executáveis
