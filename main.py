import cv2 # Para capturar a câmera e mostrar as imagens
import mediapipe as mp # Presets das partes do corpo
import math # Pros calculos matemáticos

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

    mp_drawing.draw_landmarks( # Função que desenha na tela com base nas landmarks (pontos)
        frame, # A própria imagem
        results.pose_landmarks, # Contém todos os 33 pontos do corpo, cada ponto tem x,y,z e visibility como propriedades
        mp_pose.POSE_CONNECTIONS # As lista de pares de pontos que devem ser conectados
    )

    cv2.imshow("PosturAI - Camera", frame)

    # cv2.waitKey(1): espera 1 ms por alguma tecla e permite atualizar a janela
    # & 0xFF: garante compatibilidade para ler teclas corretamente em qualquer sistema
    # ord('q'): código ASCII da letra 'q'

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break # Se a tecla 'q' for pressionada, encerra o loop principal

cam.release() # Quando iniciamos o programa prendemos a camera, com release "soltamos" ela
cv2.destroyAllWindows() #Fecha todas as abas relacionadas a aplicação



