import cv2 # Para capturar a câmera e mostrar as imagens 
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos

import matplotlib.pyplot as plt # Pra plotar os graficos de uso
import pandas as pd # Pra fazer a leitura dos dados em csv

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

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
cv2.setUseOptimized(True)                # Ativa otimizações do próprio OpenCV
cv2.setNumThreads(4)                     # Começa a processar certas operações de forma assincrona, deixando também mais rapido o inicio

# Definimos a resolução da webcam (largura e altura)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  

frame_index = 0  # Como os landmarks (marcacoes do corpo) comecam instaveis, ele nao mostra os primeiros (deixando mais rapido)

try: # Tenta executar a tarefa
    definir_icone_janela("logo-posturAI.ico") # Chama a função que muda a imagem da janela do projeto
except Exception as e: # Se algo ocorrer, retorna uma mensagem
    print("Erro ao definir ícone:", e)

# Cria ou zera o arquivo CSV a cada execução
with open("uso_postura.csv", "w", encoding="utf-8") as f:
    f.write("frame,frente,tras,lateral,distancia\n")

try:
    while True: # Toda aplicação de visão computacional roda em cima desse loop

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

        # Salva o registro do frame no CSV
        with open("uso_postura.csv", "a", encoding="utf-8") as f:
            f.write(f"{frame_index},{int(postura_frente_ruim)},{int(postura_tras_ruim)},{int(postura_lateral_ruim)},{int(postura_distancia_ruim)}\n")

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
            break

except Exception as e: # Se o loop inteiro der algum problema ele da um aviso
    print("Erro inesperado no loop:", e)

# Fecha a webcam
cam.release()

# Fecha as abas abertas pelo OpenCV
cv2.destroyAllWindows()

# ===================== RELATÓRIO GRÁFICO APRIMORADO + PERCENTUAIS =====================
try:
    from matplotlib.offsetbox import AnchoredOffsetbox, VPacker, TextArea # Importa classes para criar as caixas flutuantes do gráfico

    dados = pd.read_csv("uso_postura.csv") # Lê o arquivo CSV que a gente cria quando inicia o sistema

    # --------- Calculo das porcentagens ---------

    total_frames = len(dados)  # Total de frames analisados durante a transimissão

    perc_frente = (dados["frente"].sum() / total_frames) * 100  # % de inclinação pra frente
    perc_tras = (dados["tras"].sum() / total_frames) * 100  # % de inclinação pra trás
    perc_lateral = (dados["lateral"].sum() / total_frames) * 100  # % de inclinação lateral
    perc_distancia = (dados["distancia"].sum() / total_frames) * 100  # % de dintancia do usuario

    # Define postura "boa" quando não há nenhuma inclinação detectada (ou seja, apenas 0s)
    dados["boa"] = (
        (dados["frente"] == 0) &
        (dados["tras"] == 0) &
        (dados["lateral"] == 0) &
        (dados["distancia"] == 0)
    ).astype(int) # Interpreta esses zeros como ints

    perc_boa = (dados["boa"].sum() / total_frames) * 100 # % de postura certa
    perc_ruim = 100 - perc_boa # % total de postura ruim

    # ---------------- GRÁFICO ----------------

    plt.figure(figsize=(12, 7)) # Tamanho da figura do gráfico

    plt.plot(dados["frame"], dados["frente"], label="Frente", linewidth=2) # Linha azul do gráfico (frente)
    plt.plot(dados["frame"], dados["tras"], label="Trás", linewidth=2) # Linha laranja do gráfico (tras)
    plt.plot(dados["frame"], dados["lateral"], label="Lateral", linewidth=2) # Linha verde do gráfico (lateral)
    plt.plot(dados["frame"], dados["distancia"], label="Distância", linewidth=2) # Linha roxa do gráfico (distante)

    # Informações do plot, como o Título do grafico e as info dos eixos x e y
    plt.title("Relatório de Uso do Sistema PosturAI", fontsize=16, fontweight="bold") # Título
    plt.xlabel("Frame", fontsize=13) # Label do eixo X
    plt.ylabel("Postura Ruim (1 = sim)", fontsize=13) # Label do eixo Y

    plt.ylim(-0.1, 1.1)  # Limites do eixo Y
    plt.yticks([0, 1], ["Boa", "Ruim"])  # Converte binario para texto (0,1) pra (sim,nao)
    plt.grid(True, linestyle="--", alpha=0.3)  # Ativa a borda

    # ================== LEGENDA ORIGINAL ==================
    leg = plt.legend(
        loc="upper left",          # Posição no canto superior esquerdo
        bbox_to_anchor=(1.06, 1.0),  # Joga pra fora do gráfico
        borderaxespad=0,            # Remove o espaçamento que sobra
    )

    cor_borda = "#616161" # Cor ajustavel da borda da legenda

    leg.get_frame().set_edgecolor(cor_borda) # Define cor da borda da legenda
    leg.get_frame().set_linewidth(1.4) # Espessura da borda
    leg.get_frame().set_boxstyle("square", pad=0.6) # Estilo da caixa (quadrada)

    legend_width = leg.get_frame().get_width()  # pega a largura da caixa da legenda

    # ================= BLOCO DAS PORCENTAGENS ==================++

    cores = {
        "boa": (0, 0.6, 0),                 # Cor verde
        "frente": (0.121, 0.466, 0.705),    # Azul
        "tras": (1.0, 0.498, 0.054),        # Laranja
        "lateral": (0.172, 0.627, 0.172),   # Verde
        "distancia": (0.5, 0.0, 0.5),       # Roxo
        "ruim": (0.8, 0, 0)                 # Vermelho
    }

    # Padronização das linhas, com as variáveis de porcentagem e as cores antes estabelecidas
    linhas = [
        (f"Postura Boa: {perc_boa:.1f}%", cores["boa"]),                      # Linha Verde
        (f"Inclinação Frente: {perc_frente:.1f}%", cores["frente"]),          # Linha azul
        (f"Inclinação Trás: {perc_tras:.1f}%", cores["tras"]),                # Linha laranja
        (f"Inclinação Lateral: {perc_lateral:.1f}%", cores["lateral"]),       # Linha verde
        (f"Distância Incorreta: {perc_distancia:.1f}%", cores["distancia"]),  # Linha roxa
        (f"Postura Ruim Total: {perc_ruim:.1f}%", cores["ruim"]),             # Linha vermelha
    ]

    items = [] # Lista onde cada linha colorida será inserida
    for texto, cor in linhas:
        items.append(
            TextArea(texto, textprops=dict(color=cor, fontsize=11))  # Cria a caixa de texto colorida
        )

    box = VPacker(children=items, align="left", pad=0, sep=4)  # Empilha os itens da caixa verticalmente com espaçamento de 4px

    caixa = AnchoredOffsetbox(
        loc="upper left",                     # Posição relativa
        child=box,                            # Conteúdo é o empilhamento vertical
        pad=0.4,                              # Padding interno
        borderpad=0.6,                        # Padding da borda
        frameon=True,                         # Ativa a borda ao redor
        bbox_to_anchor=(1.05, 0.78),          # Alinhamento lateral e deslocamento vertical
        bbox_transform=plt.gca().transAxes,   # Transforma para coordenadas do gráfico
    )

    caixa.patch.set_edgecolor(cor_borda)      # Coloca mesma borda da legenda
    caixa.patch.set_linewidth(1.4)            # Mesma espessura de borda
    caixa.patch.set_facecolor("white")        # Fundo branco
    caixa.patch.set_boxstyle("square", pad=0.6) # Formato da caixa

    caixa.patch.set_width(legend_width)  # Força a mesma largura da caixa da legenda

    plt.gca().add_artist(caixa)  # Adiciona a caixa no gráfico

    plt.subplots_adjust(right=0.75) # Abre espaço na direita pra caber as caixas 
    plt.show() # Finalmente exibe o gráfico

except Exception as e:
    print(e, "Não foi possível exibir o gráfico") # Pega erros printa uma mensagem de precaução
