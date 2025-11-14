import cv2 # Para capturar a câmera e mostrar as imagens
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos

historico_projecao = []  # lista para suavizar os valores
TAMANHO_JANELA = 10 # Como se fosse uma janela, você só vê o que está dentro dela, e o que está fora desaparece.

SENSIBILIDADE_PROJECAO = 0.07 # Limite que diferencia a cabeça normal da inclinada (usando nariz/orelhas)

contador_postura_ruim = 0 
LIMITAR_FRAMES = 30  # 1 segundo = 15fps

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

        projecao = ((ombro_dir.z + ombro_esq.z) / 2) - cabeca.z # Mede a diferença entre a media dos ombros e a inclinação da cabeça

        historico_projecao.append(projecao)

        # Deixa o historico de projeção com 5 numeros, removendo os demais caso passe de 5
        if len(historico_projecao) > TAMANHO_JANELA:
            historico_projecao.pop(0)

        # Calcula a média suavizada usando a lista historico_projecao
        projecao_suave = sum(historico_projecao) / len(historico_projecao)
        print("projecao:", projecao, " | suave:", projecao_suave)

        # Verificação da distancia entre os ombros e o nariz não eram o suficiente então precisei das orelhas também
        orelha_esq = landmarks[mp_pose.PoseLandmark.LEFT_EAR]
        orelha_dir = landmarks[mp_pose.PoseLandmark.RIGHT_EAR]

        # Calcula a distância entre a orelha e o nariz, que mudam por conta da inclinação da cabeça
        diferenca_y = ((orelha_esq.y + orelha_dir.y) / 2) - cabeca.y

        # Verifica a postura usando o nariz (cabeca) e a orelha
        cabeca_inclinada_por_angulo = diferenca_y > SENSIBILIDADE_PROJECAO

        # Define a detecção final
        cabeca_final = cabeca_inclinada_por_angulo

        # ===========================================================

        # Soma os frames com a postura ruim e os zera caso melhore
        if cabeca_final:
            contador_postura_ruim += 1
        else:
            contador_postura_ruim = 0  
            historico_projecao.clear()

        # Só confirma a cabeça projetada se ficar ruim por X frames seguidos (definidos la em cima)
        cabeca_final_estavel = contador_postura_ruim >= LIMITAR_FRAMES

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
        historico_projecao.clear()

    cv2.imshow("PosturAI - Camera", frame)

    # cv2.waitKey(1): espera 1 ms por alguma tecla e permite atualizar a janela
    # & 0xFF: garante compatibilidade para ler teclas corretamente em qualquer sistema
    # ord('q'): código ASCII da letra 'q'

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break # Se a tecla 'q' for apertada, encerra o loop principal

cam.release() # Quando iniciamos o programa prendemos a camera, com release "soltamos" ela
cv2.destroyAllWindows() #Fecha todas as abas relacionadas a aplicação

