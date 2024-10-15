
# Minicurso: Configurando o Ambiente Python com `venv` (Linux/MacOS)

Este guia ensina como configurar um ambiente virtual para Python usando o módulo `venv`, garantindo que as bibliotecas e dependências do projeto sejam isoladas e organizadas.

## Pré-requisitos

- **Python 3.10+** instalado na máquina.
  - Você pode verificar a versão instalada com o comando:

    ```bash
    python3 --version
    ```

- **PIP** (Python Package Installer) já instalado.
  - Verifique a instalação do `pip`:

    ```bash
    pip --version
    ```

## Passos para Configurar o Ambiente

### 1. Criar uma Pasta para o Projeto

Escolha um local no seu sistema onde deseja criar a aplicação e crie uma pasta para o projeto:

```bash
mkdir nome_do_projeto
cd nome_do_projeto
```

### 2. Criar o Ambiente Virtual

Dentro da pasta do projeto, execute o seguinte comando para criar o ambiente virtual:

```bash
python3 -m venv venv
```

Isso criará uma pasta chamada `venv` onde serão armazenadas todas as dependências do projeto.

### 3. Ativar o Ambiente Virtual

Agora, você precisa ativar o ambiente virtual:

```bash
source venv/bin/activate
```

Após a ativação, o terminal mostrará algo como `(venv)` antes do cursor, indicando que o ambiente está ativo.

### 4. Instalar Dependências

Com o ambiente virtual ativo, instale as bibliotecas que deseja utilizar no projeto.

```bash
pip install -r dependencies.txt
```


### 5. Desativar o Ambiente Virtual

Quando terminar de trabalhar, você pode desativar o ambiente virtual com o comando:

```bash
deactivate
```

---

## Troubleshooting

- **Python não é reconhecido como comando**: Verifique se o Python está corretamente instalado e incluído no seu `PATH`.
- **Erros na ativação**: Verifique as permissões do arquivo `activate` e ajuste as permissões de execução, se necessário:

  ```bash
  chmod +x venv/bin/activate
  ```

---

## Exportando Dependências

Se você instalou mais dependências e deseja exportá-las, utilize o seguinte comando:

```bash
pip freeze > dependencies.txt
```
