import cv2 # Para capturar a câmera e mostrar as imagens
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos

# Determina um número maximo de 5 de caracteres pra lista, removendo com pop caso supere o limite
def atualizar_historico(lista, valor, limite):
    lista.append(valor)
    if len(lista) > limite:
        lista.pop(0)

historico_frontal = []  # Lista para suavizar os valores
historico_lateral = []  # Mesma coisa

TAMANHO_JANELA_FRONTAL = 10 # Como se fosse uma janela, você só vê o que está dentro dela, e o que está fora desaparece.
TAMANHO_JANELA_LATERAL = 10 # Mesma coisa

SENSIBILIDADE_PROJ_FRONTAL = 0.08 # Limite que diferencia a cabeça normal da inclinada
SENSIBILIDADE_PROJ_LATERAL = 0.03 # Mesma coisa

LIMIAR_SUAVIZACAO_LATERAL = 0.6 # Percentual minimo de inclinacao lateral para confirmar postura ruim

contador_postura_ruim = 0 

LIMIAR_FRAMES_FRONTAL = 30 # 1 segundo = 15fps
LIMIAR_FRAMES_LATERAL = 60 # Mesma coisa

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

        # Usa função auxiliar pra 
        atualizar_historico(historico_frontal, projecao, TAMANHO_JANELA_FRONTAL)

        # Calcula a média suavizada usando a lista historico_projecao
        projecao_frontal_suave = sum(historico_frontal) / len(historico_frontal)
        #print("projecao:", projecao, " | suave:", projecao_frontal_suave) Debug pra calibrar a projeção frontal

        # Calcula a distância entre a orelha e o nariz, que mudam por conta da inclinação da cabeça
        diferenca_y = cabeca.y - ((orelha_esq.y + orelha_dir.y) / 2)

        # Verifica a postura usando o nariz (cabeca) e a orelha
        cabeca_inclinada_por_angulo = diferenca_y > SENSIBILIDADE_PROJ_FRONTAL

        # ============ Verificação de Inclinação Lateral ================

        dif_lateral = abs(orelha_esq.y - orelha_dir.y) # Mede a diferença entre a altura das olheiras e mantem o valor sempre positivo com abs

        cabeca_inclinada_lateral = dif_lateral > SENSIBILIDADE_PROJ_LATERAL # Verifica se a cabeça esta inclinada com base na sensibilidade

        # Usando a função auxiliar pra manter somente 5 nums na lista
        atualizar_historico(historico_lateral, 1 if cabeca_inclinada_lateral else 0, TAMANHO_JANELA_LATERAL)

        media_lateral = sum(historico_lateral) / len(historico_lateral) # Calcula a média na lista de projeção

        cabeca_lateral_estavel = media_lateral > LIMIAR_SUAVIZACAO_LATERAL

        # Verificação da direção da inclinação da cabeça
        if cabeca_inclinada_lateral:
            if orelha_esq.y < orelha_dir.y:
                direcao = "esquerda"
            else:
                direcao = "direita"
        else:
            direcao = None

        if cabeca_lateral_estavel and direcao:
            cv2.putText(frame, f"Cabeca inclinada para {direcao}",
                (30, 150), cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 255), 2)

        # Soma os frames com a postura ruim e os zera caso melhore
        if cabeca_inclinada_por_angulo:
            contador_postura_ruim += 1
        else:
            contador_postura_ruim = 0  
            historico_frontal.clear()

        # Só confirma a cabeça projetada se ficar ruim por X frames seguidos (definidos la em cima)
        cabeca_final_estavel = contador_postura_ruim >= LIMIAR_FRAMES_FRONTAL

        # ===============================================================

        if cabeca_final_estavel: 
            cv2.putText(frame, "Cabeca projetada para frente", # Insere um texto dentro da imagem
                        (30, 100), cv2.FONT_HERSHEY_SIMPLEX, # Utiliza as coordenadas (x,y) pra ajeitar o lugar, escolhendo também a fonte
                        1.0, (0, 0, 255), 2) # Aqui são configurações do texto (tamanho, cor, espessura)

        mp_drawing.draw_landmarks( # Função que desenha na tela com base nas landmarks (pontos)
            frame, # A própria imagem
            results.pose_landmarks, # Contém todos os 33 pontos do corpo, cada ponto tem x,y,z e visibility como propriedades
            mp_pose.POSE_CONNECTIONS # As lista de pares de pontos que devem ser conectados
        )

    else:
        # Caso o usuário saia da câmera ele limpa o histórico de posturas, evitando um aviso desnecessário na tela
        contador_postura_ruim = 0
        historico_frontal.clear()
        historico_lateral.clear()

    cv2.imshow("PosturAI - Camera", frame)

    # cv2.waitKey(1): espera 1 ms por alguma tecla e permite atualizar a janela
    # & 0xFF: garante compatibilidade para ler teclas corretamente em qualquer sistema
    # ord('q'): código ASCII da letra 'q'

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break # Se a tecla 'q' for apertada, encerra o loop principal

cam.release() # Quando iniciamos o programa prendemos a camera, com release "soltamos" ela
cv2.destroyAllWindows() #Fecha todas as abas relacionadas a aplicação

