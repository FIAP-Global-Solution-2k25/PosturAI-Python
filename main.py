import cv2 # Para capturar a câmera e mostrar as imagens 
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos
import pandas as pd # Pra leitura do arquivo csv

# ======== Funções auxiliares ========

# Determina um número maximo de caracteres pra lista, removendo com pop caso supere o limite
def atualizar_historico(lista, valor, limite):
    lista.append(valor)
    if len(lista) > limite:
        lista.pop(0)

# Calcula a média de listas pra saber se o usuário está mais tempo torto do que normal
def media(lista):
    return sum(lista) / len(lista) if len(lista) > 0 else 0

# Faz a atualização do historico e calcula a média 
def atualizar_e_media(lista, valor, limite):
    atualizar_historico(lista, valor, limite)
    return sum(lista) / len(lista)

# Limpa as listas de histórico
def limpar_historicos():
    historico_frontal.clear()
    historico_lateral.clear()
    historico_tras.clear()

# ===================== Barra de status elegante no topo =====================

def desenhar_barra_status(frame, status_dict):
    # Variavel que futuramente será usada pra calcular o meio da tela pra adicionar os textos
    largura = frame.shape[1]

    # Fundo quase transparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (largura, 55), (0, 0, 0), -1)
    frame[:] = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

    # Coleta do dicionario de problemas ergonometricos e appenda pra depois exibir na tela
    textos = []
    if status_dict["frente"]:
        textos.append("Frente")
    if status_dict["tras"]:
        textos.append("Tras")
    if status_dict["lateral"]:
        textos.append("Lateral")
    if status_dict["distancia"]:
        textos.append("Longe")

    # Adiciona entre as posturas ruins uma barra vertical, se não, postura ok
    texto_final = " | ".join(textos) if textos else "Postura OK"

    # Aqui vão entrar os comandos da integração com o arduino
    # Cria uma funcao especifica pra chamar o arduino e chama ela aqui dentro

    # Define as cores dos textos, se tiver um item na lista vermelho, se não postura ta boa (cor verde)
    cor = (0, 0, 255) if textos else (0, 255, 0)

    # Linha pra falar pro OpenCV quanto o texto vai ocupar na tela
    (w, h), _ = cv2.getTextSize(texto_final, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

    # Centralização perfeita no eixo X
    x = (largura - w) // 2

    # Posição Y (altura ajustavel)
    y = 38

    # Por fim, o texto final, mostrando o frame a ser escrito, o texto, as posições de x e y
    # A fonte, o tamanho da fonte, a cor e a espessura
    cv2.putText(frame, texto_final, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, cor, 2)

# ================================================================================

# Função Always on top (deixar como se fosse um z index em 1000)
import win32gui
import win32con

def always_on_top():
    hwnd = win32gui.FindWindow(None, "PosturAI - Camera")
    if hwnd != 0:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
# ================================================================================

# ===================== Ícone personalizado da janela =====================
import win32gui
import win32con
import win32api

# Cria a janela antes de tudo (OpenCV só cria no primeiro imshow)
cv2.namedWindow("PosturAI - Camera", cv2.WINDOW_NORMAL)

def definir_icone_janela(caminho_icone):
    hwnd = win32gui.FindWindow(None, "PosturAI - Camera")
    if hwnd:
        icon = win32gui.LoadImage(
            None,
            caminho_icone,
            win32con.IMAGE_ICON,
            0, 0,
            win32con.LR_LOADFROMFILE
        )
        # Define ícone grande e pequeno da janela
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, icon)
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon)
# ========================================================================

# Lista para suavizar os valores
historico_frontal = []  
historico_lateral = []  
historico_tras = [] 

# Como se fosse uma janela, você só vê o que está dentro dela, e o que está fora desaparece.
TAMANHO_JANELA_FRONTAL = 5 
TAMANHO_JANELA_LATERAL = 20
TAMANHO_JANELA_TRAS = 6

# Limite que diferencia a cabeça normal da inclinada
SENSIBILIDADE_PROJ_FRONTAL = 0.08 
SENSIBILIDADE_PROJ_LATERAL = 0.02 
SENSIBILIDADE_PROJ_TRAS = 0.001    

contador_postura_ruim = 0 

# 1 segundo = 15fps
LIMIAR_FRAMES_FRONTAL = 30 
LIMIAR_FRAMES_LATERAL = 30 
LIMIAR_FRAMES_TRAS = 30 

buffer_registros = []

mp_pose = mp.solutions.pose              # Acesso ao modulo de poses
pose = mp_pose.Pose(
    model_complexity=0,          # Define a complexidade do modelo, quanto menor, mais rapida a inicialização
    static_image_mode=False,     # Analisa o video em tempo real e não só imagens estáticas
    enable_segmentation=False,   # Separa o que é fundo do que é corpo, mais pra alterar fundo e coisas mais decorativas (reduz desempenho)
    smooth_landmarks=True        # Remove tremidas, evita alguns falsos positivos e deixa mais estavel
)

try: # Tenta realizar a abertura da webcam
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Abre a webcam principal

    if not cam.isOpened(): # Caso ela não tenha sido aberta, da um raise com uma mensagem educativa
        raise Exception("Erro ao abrir a câmera.")
    
except Exception as e: # Qualquer outro problema exceto o da má abertura da câmera resultará em outro print
    print("Falha ao inicializar webcam:", e)
    exit()

cv2.setUseOptimized(True)                # Ativa otimizações do próprio OpenCV
cv2.setNumThreads(4)                     # Começa a processar certas operações de forma assincrona, deixando também mais rapido o inicio

# Definimos a resolução da webcam (largura e altura)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  

mp_pose = mp.solutions.pose              # Acesso ao modulo de poses
pose = mp_pose.Pose(
    model_complexity=0,          # Define a complexidade do modelo, quanto menor, mais rapida a inicialização
    static_image_mode=False,     # Analisa o video em tempo real e não só imagens estáticas
    enable_segmentation=False,   # Separa o que é fundo do que é corpo, mais pra alterar fundo e coisas mais decorativas (reduz desempenho)
    smooth_landmarks=True        # Remove tremidas, evita alguns falsos positivos e deixa mais estavel
)

frame_index = 0  # Como os landmarks (marcacoes do corpo) comecam instaveis, ele nao mostra os primeiros (deixando mais rapido)

try: # Tenta executar a tarefa
    definir_icone_janela("logo-posturAI.ico") # Chama a função que muda a imagem da janela do projeto
except Exception as e: # Se algo ocorrer, retorna uma mensagem
    print("Erro ao definir ícone:", e)

# Cria ou zera o arquivo CSV a cada execução
with open("uso_postura.csv", "w", encoding="utf-8") as f:
    f.write("frame,frente,tras,lateral,distancia\n")

parar = False

try:
    while not parar: # Toda aplicação de visão computacional roda em cima desse loop

        try:
            sucesso, frame = cam.read() 
            # frame é a imagem atual
            # sucesso retorna true se a captura funcionou
            
            if not sucesso: # Se não funcionar ela quebra o loop
                continue

        except Exception as e: # Caso ocorra algo inesperado, retorna um aviso
            print("Erro ao capturar frame:", e)
            continue

        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # O media pipe usa RGB e o OpenCV BGR, então aqui convertemos

        try:
            results = pose.process(imgRGB) # Processa as poses usando a comversão de BGR pra RGB
        except Exception as e:
            print("Erro no processamento MediaPipe:", e)
            continue

        # Indicadores de postura, sendo true pra posturas erradas (tortas mesmo)
        postura_frente_ruim = False
        postura_tras_ruim = False
        postura_lateral_ruim = False
        postura_distancia_ruim = False 

        if results.pose_landmarks: # Achou o corpo pra demarcar?
            landmarks = results.pose_landmarks.landmark # Sim, então podemos acessar os pontos

            #============= Projeção da cabeça pra frente ============
            cabeca = landmarks[mp_pose.PoseLandmark.NOSE] # Pega a cabeça (nariz)
            orelha_esq = landmarks[mp_pose.PoseLandmark.LEFT_EAR] # Pega a orelha esquerda
            orelha_dir = landmarks[mp_pose.PoseLandmark.RIGHT_EAR] # Orelha direita

            # Calculamos a diferença do eixo y da cabeca (na verdade do nariz) com a média das orelhas
            diferenca_y = cabeca.y - ((orelha_esq.y + orelha_dir.y) / 2)

            # Comparamos o resultado anterior com a sensibilidade que definimos 
            # Que acima dele, podemos dizer que a postura esta torta
            cabeca_inclinada_por_angulo = diferenca_y > SENSIBILIDADE_PROJ_FRONTAL

            # Se o resultado acima der true, ele define a variável de postura como ruim
            if cabeca_inclinada_por_angulo:
                postura_frente_ruim = True

            #======== Projeção da cabeça pra trás ================
            # A mais dificil de todas, tentei de inúmeras maneiras e essa foi a que mais trouxe resultado
            
            # Tiramos a média da altura das orelhas
            media_orelhas = ((orelha_esq.y + orelha_dir.y) / 2)

            # Se a cabeça ta um pouco acima das orelhas então a pessoa ta inclinada
            inclinacao_y_tras = cabeca.y < media_orelhas - 0.001 # Quanto menores os valores mais pra cima

            # Pegamos as landmarks dos ombros (os pontos que marcam eles)
            ombro_esq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            ombro_dir = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            # Quando a cabeça estiver mais pra frente que qualquer um dos ombros retorna true
            inclinacao_z_tras = (
                cabeca.z > ombro_esq.z + 0.005 or
                cabeca.z > ombro_dir.z + 0.005
            )

            # Definimos as landmarks dos quadris
            quadril_esq = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            quadril_dir = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

            # Função trabalhosa demais, ela calcula o angulo formado entre a, b e c (cabeca, orelha, quadril)
            def angulo(a, b, c):

                #   a
                #     \
                #      b        
                #     /
                #    c

                ab = (a.x - b.x, a.y - b.y) # Pega o vetor AB do angulo
                cb = (c.x - b.x, c.y - b.y) # Pega o vetor CB do angulo

                produto_escalar = ab[0] * cb[0] + ab[1] * cb[1] # Calculo pra ver o quanto eles apontam pra mesma direção

                mod_ab = math.sqrt(ab[0]**2 + ab[1]**2) # Tamanho do vetor AB (Módulo AB)
                mod_cb = math.sqrt(cb[0]**2 + cb[1]**2) # Tamanho do vetor CB (Módulo CB)

                if mod_ab * mod_cb == 0: # Se eles tiverem angulo zero, não da pra calcular o angulo
                    return 180
                
                cosseno = produto_escalar / (mod_ab * mod_cb) # Cosseno do angulo B
                cosseno = min(1, max(-1, cosseno)) # Limita o valor pra arredondar bonitinho
                return math.degrees(math.acos(cosseno)) # Converte em gráus e retorna


            ang_esq = angulo(cabeca, orelha_esq, quadril_esq) # Pega o angulo entre a cabeca, orelha esq e quadril esq
            ang_dir = angulo(cabeca, orelha_dir, quadril_dir) # Pega o angulo entre a cabeca, orelha dir e quadril dir

            # Se qualquer um dos lados estiver acima de 160 gráus, quer dizer que a cabeça ta muito alinhada com o tronco
            # Normalmente mostra que está inclinado pra trás
            inclinacao_angulo_tras = (ang_esq > 160 or ang_dir > 160)

            # Se qualquer uma das condicionais que indicam se tem alguma variação na sua postura forem True, você está torto
            cabeca_inclinada_para_tras_frame = (
                inclinacao_y_tras or
                inclinacao_z_tras or
                inclinacao_angulo_tras
            )
            # Pega a média dos frames da lista de historico 
            media_tras = atualizar_e_media(
                historico_tras,
                1 if cabeca_inclinada_para_tras_frame else 0,
                TAMANHO_JANELA_TRAS
            )

            # Se a média dos ultimos frames forem maiores que o valor 0.8 são ditos como inclinados
            cabeca_inclinada_para_tras_estavel = media_tras > 0.08

            # Atribui a variavel postura_tras_ruim como True 
            if cabeca_inclinada_para_tras_estavel:
                postura_tras_ruim = True

            # ========= Projeção lateral de cabeça ================

            # Calcula a diferença entre a altura das orelhas (somente valores positivos por conta do abs)
            dif_lateral = abs(orelha_esq.y - orelha_dir.y)

            # Compara o dif_lateral com a sensibilidade que pre-definimos no inicio do sistema
            cabeca_inclinada_lateral = dif_lateral > SENSIBILIDADE_PROJ_LATERAL

            # Atualiza a lista de historico de acordo com o tamanho maximo e faz a média entre os frames tortos e normais
            media_lateral = atualizar_e_media(
                historico_lateral,
                1 if cabeca_inclinada_lateral else 0,
                TAMANHO_JANELA_LATERAL
            )

            # Caso a média dos frames sejam maiores que 0.6, eles estão inclinados
            cabeca_lateral_estavel = media_lateral > 0.6

            # Caso seja true, atribui a variavel o valor
            if cabeca_lateral_estavel:
                postura_lateral_ruim = True

            # ========== Calculo da distância do usuário ==============

            # Calcula a diferença no eixo x (horizontal) entre as orelhas dir e esq
            dist_orelhas = abs(orelha_esq.x - orelha_dir.x)

            # Caso a dist_orelhas seja menor que 0.15, o user ta muito longe do dispositivo
            if dist_orelhas < 0.15:
                postura_distancia_ruim = True

            # Se a cabeça estiver inclinada pra frente é atribuida a contagem na variavel de contagem
            if cabeca_inclinada_por_angulo: 
                contador_postura_ruim += 1
            # Caso contrario, limpamos o histórico
            else:
                contador_postura_ruim = 0  
                historico_frontal.clear()

            # Só da alerta de instabilidade quando as ocorrencias de postura correspondam a quantidade de frames
            # Que definimos para diferenciar uma postura boa ou ruim
            cabeca_final_estavel = contador_postura_ruim >= LIMIAR_FRAMES_FRONTAL

            # Só depois disso tudo afirmamos que a postura está de fato ruim (pra projeções frontais)
            if cabeca_final_estavel:
                postura_frente_ruim = True

        # Se ele não achar um corpo pra identificar as partes ele limpa o histórico tbm
        else:
            contador_postura_ruim = 0
            limpar_historicos()

        # Se os valores do dicionario forem True, vão ser coletados pra serem printados em tela
        status_postura = {
            "frente": postura_frente_ruim,
            "tras": postura_tras_ruim,
            "lateral": postura_lateral_ruim,
            "distancia": postura_distancia_ruim
        }

        buffer_registros.append([
            frame_index,
            int(postura_frente_ruim),
            int(postura_tras_ruim),
            int(postura_lateral_ruim),
            int(postura_distancia_ruim)
        ])

        try:
            desenhar_barra_status(frame, status_postura) # Função que coleta o status_postura e caso sejam True, são printados

        except Exception as e: # Exibe mensagem de erro caso algo dê errado
            print("Erro ao desenhar a barra:", e)

        # Nome da aba do windows que abre junto com a câmera
        cv2.imshow("PosturAI - Camera", frame)

        # Always on top ativo
        always_on_top()

        # Contador de frames processados (útil para debug)
        frame_index += 1

        # Caso o usuário aperte a tecla 'q' ele quita do sistema
        if cv2.waitKey(1) & 0xFF == ord('q'):
            parar = True
            break

except Exception as e: # Se o loop inteiro der algum problema ele da um aviso
    print("Erro inesperado no loop:", e)

# Fecha a webcam
cam.release()

# Fecha as abas abertas pelo OpenCV
cv2.destroyAllWindows()
cv2.waitKey(1)
cv2.waitKey(1)

df = pd.DataFrame(
    buffer_registros,
    columns=["frame","frente","tras","lateral","distancia"]
)
df.to_csv("uso_postura.csv", index=False)

# ===================== Gráfico 3D =====================

# Otimização pra carregar mais rapido as bibliotecas 
from numpy import array, append, deg2rad
from matplotlib.pyplot import figure, subplot, show, title, subplots_adjust

dados = pd.read_csv("uso_postura.csv")

# Total de frames processados para calcular os percentuais
total_frames = len(dados)

# Calcula o percentual de postura ruim para cada categoria
perc_frente = (dados["frente"].sum() / total_frames) * 100
perc_tras = (dados["tras"].sum() / total_frames) * 100
perc_lateral = (dados["lateral"].sum() / total_frames) * 100
perc_dist = (dados["distancia"].sum() / total_frames) * 100

# ======== DADOS REAIS PARA O O RADAR ========

# Labels organizados para respeitar a posição no gráfico (cima, direita, baixo, esquerda)
labels = ["Frente", "Distância", "Trás", "Lateral"]

# Valores associados pra cada label na mesma ordem
values = [perc_frente, perc_dist, perc_tras, perc_lateral]

# Converte a lista em um array do np e adiciona o primeiro valor no final pra fechar o gráfico
values = array(values, dtype=float)
values = append(values, values[0])

# Define manualmente os angulos para colocar cada label exatamente onde eu queria
angles = deg2rad([90, 0, 270, 180, 90])

# ======== IMAGEM ========

# Define o tamanho da imagem do gráfico
fig = figure(figsize=(4, 4))

# Cria o gráfico polar, com o circulo parecendo um radar 
ax = subplot(111, polar=True) # 111 significa 1 linha, 1 coluna, posição 1.

# Cor do fundo do gráfico
ax.set_facecolor("#f6f7fa")

# Posiciona os textos em volta do radar conforme os ângulos que definimos acima
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=11, color="gray")

# Define a escala do eixo radial (círculos internos)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(["", "", "", "", ""]) # Tiramos os números pra ficar mais bonito

# Ajusta a beleza dos marcadores (ticks)
ax.tick_params(axis="y", labelsize=8)

# ======== GRADIENTE DO GRÁFICO ========

# Cria o efeito de profundidade com varias camadas
for i in range(90):
    t = i / 90                 # Intensidade progressiva
    fade = values * t          # Valores multiplicados para efeito de subida
    ax.fill(angles, fade, color=(0.3, 0.0, 0.9, 0.018), zorder=i)

# Contorno principal do radar
ax.plot(angles, values, color="#6d00ff", linewidth=2)

# Preenchimento interno
ax.fill(angles, values, color=(0.4, 0.1, 0.9, 0.35))

# Marcações brancas nos pontos finais
ax.scatter(angles[:-1], values[:-1], color="white", s=40,
           edgecolor="#6d00ff", linewidth=1.5)

# Tira a borda redonda padrão do gráfico
ax.spines["polar"].set_visible(False)

# Aumenta o espaço em cima pra caber o título
subplots_adjust(top=0.78)

# Título do gráfico
title("Relatório de uso - PosturAI", fontsize=12, fontweight="bold", pad=20)

# Mostra o gráfico final
show()
