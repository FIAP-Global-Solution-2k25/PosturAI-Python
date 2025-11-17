import cv2 # Para capturar a câmera e mostrar as imagens 
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos

# ======== Funções auxiliares adicionadas (sem alterar comentários existentes) ========

def media(lista):
    return sum(lista) / len(lista) if len(lista) > 0 else 0

def escrever(frame, texto, y):
    cv2.putText(frame, texto, (30, y), cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 255), 2)

def atualizar_e_media(lista, valor, limite):
    atualizar_historico(lista, valor, limite)
    return sum(lista) / len(lista)

def limpar_historicos():
    historico_frontal.clear()
    historico_lateral.clear()
    historico_tras.clear()

# ================================================================================

# Determina um número maximo de 5 de caracteres pra lista, removendo com pop caso supere o limite
def atualizar_historico(lista, valor, limite):
    lista.append(valor)
    if len(lista) > limite:
        lista.pop(0)

# Lista para suavizar os valores
historico_frontal = []  
historico_lateral = []  
historico_tras = [] 

# Como se fosse uma janela, você só vê o que está dentro dela, e o que está fora desaparece.
TAMANHO_JANELA_FRONTAL = 10 
TAMANHO_JANELA_LATERAL = 10 
TAMANHO_JANELA_TRAS = 5 

# Limite que diferencia a cabeça normal da inclinada
SENSIBILIDADE_PROJ_FRONTAL = 0.08 
SENSIBILIDADE_PROJ_LATERAL = 0.03 
SENSIBILIDADE_PROJ_TRAS = 0.001    

contador_postura_ruim = 0 

# 1 segundo = 15fps
LIMIAR_FRAMES_FRONTAL = 30 
LIMIAR_FRAMES_LATERAL = 30 
LIMIAR_FRAMES_TRAS = 30    

mp_pose = mp.solutions.pose              # Acesso ao modulo de poses
pose = mp_pose.Pose()                    # Criação do detector de poses
mp_drawing = mp.solutions.drawing_utils  # Pra desenhar as partes do corpo

cam = cv2.VideoCapture(0) 

while True: # Toda aplicação de visão computacional roda em cima desse loop

    sucesso, frame = cam.read() 
    # frame é a imagem atual
    # sucesso retorna true se a captura funcionou
    
    if not sucesso: # Se não funcionar ela quebra o loop
        print()
        continue

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # O media pipe usa RGB e o OpenCV BGR, então aqui convertemos

    results = pose.process(imgRGB) # Processa as poses usando a comversão de BGR pra RGB

    if results.pose_landmarks: # Achou o corpo?
        landmarks = results.pose_landmarks.landmark # Sim, então podemos acessar os pontos

        # As funções a seguir acessam o corpo e com base nos presets do media pipe, os separa em partes
        
        cabeca = landmarks[mp_pose.PoseLandmark.NOSE] # Pega a cabeça (nariz)
        ombro_esq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER] # Pega o ombro esquerdo
        ombro_dir = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER] # Pega o ombro direito
        orelha_esq = landmarks[mp_pose.PoseLandmark.LEFT_EAR] # Pega a orelha esquerda
        orelha_dir = landmarks[mp_pose.PoseLandmark.RIGHT_EAR] # Pega a orelha direita

        # ============= Verificação de Inclinação Frontal ==============

        projecao = ((ombro_dir.z + ombro_esq.z) / 2) - cabeca.z # Mede a diferença entre a media dos ombros e a inclinação da cabeça

        projecao_frontal_suave = atualizar_e_media(historico_frontal, projecao, TAMANHO_JANELA_FRONTAL)

        #print("projecao:", projecao, " | suave:", projecao_frontal_suave) Debug pra calibrar a projeção frontal

        diferenca_y = cabeca.y - ((orelha_esq.y + orelha_dir.y) / 2)

        cabeca_inclinada_por_angulo = diferenca_y > SENSIBILIDADE_PROJ_FRONTAL

        # ============ Verificação de Inclinação PARA TRÁS (CORRIGIDO) ================

        cabeca_inclinada_para_tras_frame = diferenca_y < -0.001

        media_tras = atualizar_e_media(
            historico_tras,
            1 if cabeca_inclinada_para_tras_frame else 0,
            TAMANHO_JANELA_TRAS
        )

        cabeca_inclinada_para_tras_estavel = media_tras > 0.01

        if cabeca_inclinada_para_tras_estavel:
            escrever(frame, "Cabeca inclinada para tras", 200)

        # ============ Verificação de Inclinação Lateral ================

        dif_lateral = abs(orelha_esq.y - orelha_dir.y)

        cabeca_inclinada_lateral = dif_lateral > SENSIBILIDADE_PROJ_LATERAL

        media_lateral = atualizar_e_media(
            historico_lateral,
            1 if cabeca_inclinada_lateral else 0,
            TAMANHO_JANELA_LATERAL
        )

        cabeca_lateral_estavel = media_lateral > 0.6

        if cabeca_inclinada_lateral:
            if orelha_esq.y < orelha_dir.y:
                direcao = "direita"
            else:
                direcao = "esquerda"
        else:
            direcao = None

        if cabeca_lateral_estavel and direcao:
            escrever(frame, f"Cabeca inclinada para {direcao}", 150)

        # Soma os frames com a postura ruim e os zera caso melhore
        if cabeca_inclinada_por_angulo: 
            contador_postura_ruim += 1
        else:
            contador_postura_ruim = 0  
            historico_frontal.clear()

        cabeca_final_estavel = contador_postura_ruim >= LIMIAR_FRAMES_FRONTAL

        if cabeca_final_estavel:
            escrever(frame, "Cabeca projetada para frente", 100)

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    else:
        # Caso o usuário saia da câmera ele limpa o histórico de posturas, evitando um aviso desnecessário na tela
        contador_postura_ruim = 0
        limpar_historicos()

    cv2.imshow("PosturAI - Camera", frame)

    # cv2.waitKey(1): espera 1 ms por alguma tecla e permite atualizar a janela
    # & 0xFF: garante compatibilidade para ler teclas corretamente em qualquer sistema
    # ord('q'): código ASCII da letra 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break # Se a tecla 'q' for apertada, encerra o loop principal

cam.release() # Quando iniciamos o programa prendemos a camera, com release "soltamos" ela
cv2.destroyAllWindows() #Fecha todas as abas relacionadas a aplicação

