# 📘 PosturAI – Monitoramento Inteligente de Postura com Visão Computacional

O **PosturAI** é um sistema de monitoramento postural em tempo real que identifica padrões de postura inadequada, exibe alertas imediatos ao usuário e gera relatórios visuais avançados ao final da sessão.

Ele combina **Visão Computacional (MediaPipe + OpenCV)**, técnicas profundas de **otimização de desempenho** e um **gráfico Radar 3D** elegante que resume todo o comportamento postural do usuário.

---

## 🎯 Objetivo do Projeto

O PosturAI foi desenvolvido para:

- Detectar postura inadequada (frente, trás, lateral e distância).
- Exibir alertas ao usuário de forma elegante e instantânea.
- Registrar cada frame da sessão para análise posterior.
- Gerar um **relatório gráfico 3D** intuitivo.
- Suportar integração com Arduino para biofeedback vibratório.
- Oferecer experiência fluida mesmo em máquinas modestas.

---

## 🧠 Como o Sistema Funciona

### **1️⃣ Captura e Processamento em Tempo Real**

- Captura vídeo via OpenCV.
- Processa landmarks com MediaPipe Pose.
- Analisa posição da cabeça, orelhas, ombros e quadris.
- Usa lógica geométrica + profundidade + filtros temporais para:
  - Projeção frontal
  - Projeção para trás
  - Desvio lateral
  - Distância da tela

---

### **2️⃣ Alerta Visual Imediato**

A janela do app possui:
- Barra superior transparente
- Texto automático das posturas incorretas
- Cores verde/vermelho
- Modo Always-on-Top garantido via Win32
- Ícone personalizado da aplicação

---

### **3️⃣ Relatório Final em Radar 3D**

Após encerrar a captura:
- Os dados são salvos em CSV.
- Matplotlib (lazy load) gera um radar semi-3D com:
  - Gradiente suave
  - Pontos brancos
  - Título formatado
  - Labels reposicionados manualmente (topo, direita, baixo, esquerda)
  - Canvas ampliado lateralmente
- Percentuais calculados automaticamente.

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|-----------|------------|
| **Python** | Lógica geral |
| **OpenCV** | Captura de vídeo + UI |
| **MediaPipe Pose** | Identificação corporal |
| **Matplotlib** | Radar 3D final |
| **NumPy** | Cálculos numéricos |
| **Pandas** | Registro do CSV |
| **PyWin32** | Always-on-top + ícone |
| **Arduino (opcional)** | Biofeedback vibratório |

---

## 🧩 Destaques Técnicos

### ✔ **Otimização Avançada**

- Importações seletivas (`from cv2 import ...`)
- `setUseOptimized(True)`
- Threads controladas
- Lazy load do Matplotlib
- CSV gerado somente ao final
- MediaPipe carregado uma vez

### ✔ **Detecção Robusta**

- Cálculo de ângulos
- Média móvel com janelas deslizantes
- Múltiplas verificações por postura
- Tolerância reduzida para precisão

### ✔ **Interface Profissional**

- Barra superior com transparência
- Janela com ícone customizado
- Always-On-Top automático
- Layout centralizado e elegante

### ✔ **Relatório Premium**

- Radar 3D com gradiente
- Canvas expandido (left/right)
- Pontos brancos e contorno roxo
- Labels bem posicionadas

---

## 👥 Autores

- **Ulisses Ribeiro** — Desenvolvimento *core* e arquitetura técnica da solução em Visão Computacional.
- **Arthur Berlofa Bosi** — Responsável pela integração IoT (ESP32) e pela gestão de configuração via arquivos JSON.

---

## 📊 Exemplo do Relatório

O Radar exibe:

- % cabeça à frente
- % cabeça atrás
- % desvio lateral
- % distância inadequada
- Média geral de uso

Perfeito para ergonomia, saúde ocupacional e produtividade.

---

## 🔧 Instalação

```bash
pip install opencv-python
pip install mediapipe==0.10.21
pip install matplotlib
pip install pandas
pip install numpy
pip install pywin32
