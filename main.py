import cv2 # Para capturar a câmera e mostrar as imagens 
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos

# ======== Funções auxiliares adicionadas (sem alterar comentários existentes) ========

# Determina um número maximo de 5 de caracteres pra lista, removendo com pop caso supere o limite
def atualizar_historico(lista, valor, limite):
    lista.append(valor)
    if len(lista) > limite:
        lista.pop(0)

# Calcula a média de listas
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
    largura = frame.shape[1]

    # fundo translúcido da barra
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (largura, 55), (0, 0, 0), -1)
    frame[:] = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

    # compõe os textos dos alertas ativos
    textos = []
    if status_dict["frente"]:
        textos.append("Frente")
    if status_dict["tras"]:
        textos.append("Tras")
    if status_dict["lateral"]:
        textos.append("Lateral")
    if status_dict["distancia"]:
        textos.append("Longe")

    texto_final = " | ".join(textos) if textos else "Postura OK"

    # Aqui vai entrar os comandos da integração com o arduino
    # Cria uma funcao especifica pra chamar o arduino e chama ela aqui dentro

    cor = (0, 0, 255) if textos else (0, 255, 0)

    (w, h), _ = cv2.getTextSize(texto_final, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    x = (largura - w) // 2
    y = 38

    cv2.putText(frame, texto_final, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                1.0, cor, 2)

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

# Lista para suavizar os valores
historico_frontal = []  
historico_lateral = []  
historico_tras = [] 

# Como se fosse uma janela, você só vê o que está dentro dela, e o que está fora desaparece.
TAMANHO_JANELA_FRONTAL = 5 
TAMANHO_JANELA_LATERAL = 20 
TAMANHO_JANELA_TRAS = 5 

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
    model_complexity=0,          # muito mais rápido para iniciar
    static_image_mode=False,     # mantém o rastreamento contínuo
    enable_segmentation=False,   # não carrega segmentação → inicia mais rápido
    smooth_landmarks=True
)

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.setUseOptimized(True)  # ativa otimizações do OpenCV
cv2.setNumThreads(4)       # acelera operações internas, inclusive na abertura

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  

frame_index = 0  # usado para não desenhar landmarks nos primeiros frames

while True: # Toda aplicação de visão computacional roda em cima desse loop

    sucesso, frame = cam.read() 
    # frame é a imagem atual
    # sucesso retorna true se a captura funcionou
    
    if not sucesso: # Se não funcionar ela quebra o loop
        print()
        continue

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # O media pipe usa RGB e o OpenCV BGR, então aqui convertemos

    results = pose.process(imgRGB) # Processa as poses usando a comversão de BGR pra RGB

    postura_frente_ruim = False
    postura_tras_ruim = False
    postura_lateral_ruim = False
    postura_distancia_ruim = False 

    if results.pose_landmarks: # Achou o corpo?
        landmarks = results.pose_landmarks.landmark # Sim, então podemos acessar os pontos

        # As funções a seguir acessam o corpo e com base nos presets do media pipe, os separa em partes
        
        cabeca = landmarks[mp_pose.PoseLandmark.NOSE] # Pega a cabeça (nariz)
        orelha_esq = landmarks[mp_pose.PoseLandmark.LEFT_EAR] 
        orelha_dir = landmarks[mp_pose.PoseLandmark.RIGHT_EAR]

        diferenca_y = cabeca.y - ((orelha_esq.y + orelha_dir.y) / 2)
        cabeca_inclinada_por_angulo = diferenca_y > SENSIBILIDADE_PROJ_FRONTAL

        if cabeca_inclinada_por_angulo:
            postura_frente_ruim = True

        cabeca_inclinada_para_tras_frame = cabeca.y < ((orelha_esq.y + orelha_dir.y) / 2) - 0.015

        media_tras = atualizar_e_media(
            historico_tras,
            1 if cabeca_inclinada_para_tras_frame else 0,
            TAMANHO_JANELA_TRAS
        )

        cabeca_inclinada_para_tras_estavel = media_tras > 0.6

        if cabeca_inclinada_para_tras_estavel:
            postura_tras_ruim = True

        dif_lateral = abs(orelha_esq.y - orelha_dir.y)

        cabeca_inclinada_lateral = dif_lateral > SENSIBILIDADE_PROJ_LATERAL

        media_lateral = atualizar_e_media(
            historico_lateral,
            1 if cabeca_inclinada_lateral else 0,
            TAMANHO_JANELA_LATERAL
        )

        cabeca_lateral_estavel = media_lateral > 0.6

        if cabeca_lateral_estavel:
            postura_lateral_ruim = True

        dist_orelhas = abs(orelha_esq.x - orelha_dir.x)

        if dist_orelhas < 0.15:
            postura_distancia_ruim = True

        if cabeca_inclinada_por_angulo: 
            contador_postura_ruim += 1
        else:
            contador_postura_ruim = 0  
            historico_frontal.clear()

        cabeca_final_estavel = contador_postura_ruim >= LIMIAR_FRAMES_FRONTAL

        if cabeca_final_estavel:
            postura_frente_ruim = True

    else:
        contador_postura_ruim = 0
        limpar_historicos()

    status_postura = {
        "frente": postura_frente_ruim,
        "tras": postura_tras_ruim,
        "lateral": postura_lateral_ruim,
        "distancia": postura_distancia_ruim
    }

    desenhar_barra_status(frame, status_postura)

    cv2.imshow("PosturAI - Camera", frame)

    # Always on top ativo
    always_on_top()

    frame_index += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
