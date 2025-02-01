import random
import os

def sortear_naoencontrado():
    # Caminho da pasta onde estão as imagens
    caminho_pasta = "resources/poneis/Naoencontrado"  # Substitua pelo caminho correto

    # Lista todos os arquivos na pasta e filtra para manter apenas arquivos de imagem
    imagens = [arquivo for arquivo in os.listdir(caminho_pasta) if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Verifica se há imagens na pasta
    if imagens:
        imagem_sorteada = random.choice(imagens)
        return imagem_sorteada
    else:
        return "resources/poneis/semimagem.png"
    



print(type(sortear_naoencontrado()))