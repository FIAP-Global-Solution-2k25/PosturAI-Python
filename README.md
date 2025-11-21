# 🐍 PosturAI-Python: O seu Assistente de Postura com Inteligência Artificial

## 💡 Sobre o Projeto
O **PosturAI-Python** é um projeto desenvolvido no âmbito da **FIAP Global Solution 2025** com o objetivo de combater os problemas de saúde relacionados à má postura durante longas jornadas de trabalho ou estudo.

Utilizando a visão computacional e modelos de *Machine Learning* para estimativa de pose, o PosturAI monitora em tempo real a postura do usuário através da webcam, fornecendo feedback imediato para correções. A má postura é um problema crescente na era do trabalho híbrido e remoto, e este projeto visa promover o bem-estar e a **ergonomia digital**.

---

## 👥 Autores

- **Ulisses Ribeiro - RM562230** — Desenvolvimento *core* e arquitetura técnica da solução em Visão Computacional.
- **Arthur Berlofa Bosi - RM564438** — Responsável pela integração IoT (ESP32) e pela gestão de configuração via arquivos JSON.
- **Arthur Ferreira - RM564958** - Responsavel pela organização das pastas, e planejamento do software.

---

## ✨ Recursos Principais
* **Detecção de Postura em Tempo Real:** Monitoramento contínuo usando a webcam.
* **Estimativa de Pose:** Utiliza bibliotecas avançadas (como MediaPipe ou OpenPose) para mapear pontos-chave do corpo (ombros, pescoço, coluna).
* **Feedback Visual e Sonoro:** Alertas discretos quando a postura ideal não é mantida por um período de tempo.
* **Análise Ergonômica:** Avaliação de métricas chave de postura, como o alinhamento da cabeça e a curvatura da coluna.

---

## 🛠️ Tecnologias Utilizadas
O projeto é construído principalmente em Python, aproveitando o poder das seguintes bibliotecas:

* **Python 3.x**
* **OpenCV:** Para captura, exibição e processamento de vídeo da webcam.
* **MediaPipe (ou similar):** Para a estimativa de pose e detecção de *landmarks*.
* **NumPy:** Para manipulação eficiente de dados numéricos.

---

## 🚀 Instalação e Configuração

Siga os passos abaixo para ter o PosturAI-Python rodando em sua máquina:

### 1. Clonar o Repositório
```bash
git clone [https://github.com/FIAP-Global-Solution-2k25/PosturAI-Python.git](https://github.com/FIAP-Global-Solution-2k25/PosturAI-Python.git)

cd PosturAI-Python
````

### 2\. Criar e Ativar o Ambiente Virtual

É altamente recomendado o uso de um ambiente virtual para isolar as dependências.

**Criar o ambiente virtual (venv):**

```bash
python -m venv venv
```

**Ativar o ambiente virtual no macOS/Linux:**

```bash
source venv/bin/activate
```

**Ativar o ambiente virtual no Windows (Prompt de Comando ou PowerShell):**

```bash
venv\Scripts\activate
```

### 3\. Instalar as Dependências

Instale todas as bibliotecas necessárias listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4\. Executar o Aplicativo

Após a instalação, execute o script principal para iniciar o monitoramento de postura via webcam:

```bash
python main.py
# (Nota: o nome do arquivo principal pode ser ajustado conforme a estrutura final)
```

-----

## 🤝 Contribuição

Contribuições são o que tornam a comunidade de código aberto um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito apreciada**.

1.  Faça um **Fork** do Projeto.
2.  Crie uma **Branch** para sua Feature (`git checkout -b feature/NovaFuncionalidade`).
3.  Commit suas Mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`).
4.  Faça um **Push** para a Branch (`git push origin feature/NovaFuncionalidade`).
5.  Abra um **Pull Request**.

-----

## 📜 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo `LICENSE` no repositório para mais detalhes.

-----

<div align="center">
  Desenvolvido para a Global Solution 2025 da FIAP.
  Você pode encontrar mais informações sobre a Global Solution da FIAP no site oficial: [Global Solution FIAP](https://www.fiap.com.br/graduacao/global-solution/?utm_term=&utm_campaign=GRAD+-+DSA&utm_source=adwords&utm_medium=ppc&hsa_acc=3358810376&hsa_cam=21102294227&hsa_grp=158449020381&hsa_ad=737370541126&hsa_src=g&hsa_tgt=dsa-2403784242683&hsa_kw=&hsa_mt=&hsa_net=adwords&hsa_ver=3&gad_source=1&gad_campaignid=21102294227&gbraid=0AAAAADqmiBBL0vsXCBVGF-uBG2qZC6mbY&gclid=CjwKCAiAlfvIBhA6EiwAcErpyZ9ifXZTOhMagASAJJAlFp0BM2fjwkvAjUnWgSHiFA5UMkvOpMlhyhoCflUQAvD_BwE).
</div>


