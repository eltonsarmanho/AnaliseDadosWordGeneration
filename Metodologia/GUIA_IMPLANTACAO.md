# Guia de Implantação do Dashboard

## Pré-requisitos
- Ambiente local configurado com todas as dependências do projeto.
- Chave SSH válida (`.pem`) com permissões corretas (`chmod 400 caminho/para/sua-chave.pem`).
- Acesso ao servidor remoto (usuário SSH e endereço IP ou DNS).

## Passo a passo
1. Posicione-se no diretório acima da pasta do projeto (aquele que contém `AnaliseDadosWordGeneration/`).
2. Execute o comando abaixo, substituindo:
   - `caminho/para/sua-chave.pem` pela localização da sua chave SSH.
   - `seu.usuario` pelo usuário habilitado no servidor (ex.: `ec2-user`).
   - `seu.endereco.remoto` pelo IP ou DNS da instância de destino.

```bash
rsync -avz --progress \
  --exclude 'venv/' \
  --exclude 'env/' \
  --exclude '.venv/' \
  --exclude '.git/' \
  --exclude '.gitignore' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '*.pyd' \
  --exclude '.Python' \
  --exclude '*.so' \
  --exclude '*.egg' \
  --exclude '*.egg-info/' \
  --exclude 'dist/' \
  --exclude 'build/' \
  --exclude '.pytest_cache/' \
  --exclude '.vscode/' \
  --exclude '.idea/' \
  --exclude '*.log' \
  --exclude '.DS_Store' \
  --exclude 'Thumbs.db' \
  --exclude '*.swp' \
  --exclude '*.swo' \
  --exclude '*~' \
  -e "ssh -i caminho/para/sua-chave.pem" \
  AnaliseDadosWordGeneration/ \
  seu.usuario@seu.endereco.remoto:/home/seu.usuario/appStreamLit/
```

## Pós-implantação
- Acesse o servidor e reinicie o serviço do Streamlit (se aplicável) para carregar a nova versão.
- Verifique os logs do aplicativo para garantir que a atualização ocorreu sem erros.
- Execute um teste rápido na interface para confirmar o funcionamento dos principais fluxos.
