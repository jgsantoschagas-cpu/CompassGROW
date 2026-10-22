# CompassGROW — versão pessoal para iPhone

Esta versão mantém Python + Streamlit, adapta a interface para telas pequenas e salva os dados em SQLite. Também permite exportar e restaurar um backup JSON.

## 1. Rodar no computador

Requer Python 3.10 ou mais recente.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá o app. O banco `compassgrow.db` será criado na pasta do projeto.

## 2. Abrir no iPhone

Para acessar de qualquer lugar, o app precisa ser hospedado em um servidor. Depois de publicar, abra o endereço no Safari e use **Compartilhar → Adicionar à Tela de Início**.

## 3. Proteção por senha

A senha é opcional no código para facilitar o teste local. Antes de publicar na internet, configure `COMPASSGROW_PASSWORD`.

No Streamlit Community Cloud, adicione em **App settings → Secrets**:

```toml
COMPASSGROW_PASSWORD = "coloque-uma-senha-forte-aqui"
```

Não coloque a senha no código nem no GitHub.

## 4. Importante sobre hospedagem e persistência

O SQLite salva os dados no arquivo `compassgrow.db` e funciona bem localmente. Em hospedagens gratuitas, o disco local pode ser temporário ou não ser compartilhado entre reinicializações. Antes de usar como arquivo pessoal definitivo na nuvem, configure um banco persistente ou uma hospedagem com volume persistente. Use a aba **Dados** para exportar backups JSON regularmente.

O arquivo `compassgrow.db` está listado no `.gitignore` para evitar publicar seu banco pessoal no GitHub.

## 5. Publicar no Streamlit Community Cloud

1. Crie um repositório no GitHub e envie `app.py`, `requirements.txt`, `README.md` e `.gitignore`.
2. Entre em https://streamlit.io/cloud e conecte sua conta GitHub.
3. Crie um app selecionando o repositório e o arquivo `app.py`.
4. Configure a senha em **App settings → Secrets**.
5. Antes de inserir informações pessoais importantes, configure e teste armazenamento persistente.

## O que já foi melhorado

- Layout mais adequado para celular.
- Navegação simplificada em cinco áreas.
- Salvamento dos dados em SQLite entre sessões locais.
- Cálculo de progresso baseado em etapas efetivamente preenchidas.
- Histórico de ajustes com data e hora.
- Exportação e restauração de backup.
- Campo opcional de senha por variável de ambiente ou segredo do Streamlit.
