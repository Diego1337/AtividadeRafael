import os
import streamlit as st
from pymongo import MongoClient
import gridfs
from PIL import Image
import io
import numpy as np

# --- SEÇÃO DE DEPURAÇÃO (DEBUG) ---
# Isso vai aparecer no topo do app para confirmar que o 'os' foi importado
# e mostrar onde o Python está procurando a pasta.
print("Módulo OS importado com sucesso.") 
print(f"Diretório de trabalho atual: {os.getcwd()}")

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Reconhecimento Facial FEI", layout="wide")
st.title("📸 Gerenciador e Reconhecimento - MongoDB Atlas")

# --- 2. CONEXÃO COM O BANCO ---
@st.cache_resource
def get_connection():
    # URI do seu banco
    uri = "mongodb+srv://diegorlima8_db_user:04KskmDzmVNDK53t@cluster0.4nsgcvo.mongodb.net/?appName=Cluster0"
    return MongoClient(uri)

try:
    client = get_connection()
    db = client['midias']
    fs = gridfs.GridFS(db)
    st.sidebar.success("Conectado ao MongoDB Atlas!")
except Exception as e:
    st.error(f"Erro de conexão: {e}")
    st.stop()

# --- 3. FUNÇÃO MATEMÁTICA ---
def calcular_diferenca(imagem1, imagem2):
    img1_gray = imagem1.convert('L').resize((100, 100))
    img2_gray = imagem2.convert('L').resize((100, 100))
    arr1 = np.array(img1_gray)
    arr2 = np.array(img2_gray)
    return np.mean(np.abs(arr1 - arr2))

# --- 4. ÁREA DE UPLOAD (ADMIN) ---
with st.expander("📂 Carregar Imagens (Executar uma vez)"):
    st.write(f"Diretório atual: `{os.getcwd()}`")

    if st.button("Iniciar Carregamento das Imagens"):
        pasta_imagens = 'frontalimages_manuallyaligned_part1'

        # Verificação robusta do caminho
        if not os.path.exists(pasta_imagens):
            st.error(f"❌ ERRO: A pasta `{pasta_imagens}` não foi encontrada!")
            st.warning("Dica: Verifique se você descompactou a pasta de imagens DENTRO da mesma pasta onde está este arquivo app.py.")
        else:
            arquivos = [f for f in os.listdir(pasta_imagens) if f.lower().endswith('.jpg')]

            if len(arquivos) == 0:
                st.warning("A pasta existe, mas não tem arquivos .jpg dentro dela.")
            else:
                st.info(f"Processando {len(arquivos)} imagens...")
                barra = st.progress(0)
                contador = 0

                for i, nome_arquivo in enumerate(arquivos):
                    caminho = os.path.join(pasta_imagens, nome_arquivo)
                    if not fs.exists({"filename": nome_arquivo}):
                        try:
                            with open(caminho, 'rb') as f:
                                fs.put(f, filename=nome_arquivo)
                                contador += 1
                        except Exception as e:
                            st.error(f"Erro no arquivo {nome_arquivo}: {e}")
                    barra.progress((i + 1) / len(arquivos))

                st.success(f"Sucesso! {contador} imagens novas foram salvas no MongoDB.")

st.divider()

# --- 5. ÁREA DE RECONHECIMENTO (USUÁRIO) ---
st.header("🕵️ Reconhecimento Facial")
col1, col2 = st.columns([1, 2])

with col1:
    up_file = st.file_uploader("Sua foto", type=["jpg", "png"])
    if up_file:
        img_busca = Image.open(up_file)
        st.image(img_busca, width=200)

with col2:
    if up_file and st.button("🔍 Buscar Similar"):
        docs = list(fs.find())
        if not docs:
            st.warning("Banco vazio.")
        else:
            melhor_img = None
            menor_diff = float('inf')
            nome_img = ""

            bar = st.progress(0)
            for i, doc in enumerate(docs):
                try:
                    # Ler apenas se necessário (otimização básica)
                    d = doc.read()
                    curr_img = Image.open(io.BytesIO(d))
                    diff = calcular_diferenca(img_busca, curr_img)

                    if diff < menor_diff:
                        menor_diff = diff
                        melhor_img = curr_img
                        nome_img = doc.filename

                    if i % 5 == 0: bar.progress((i+1)/len(docs))
                except: pass

            bar.empty()
            st.success(f"Encontrado! Diferença: {menor_diff:.2f}")
            st.write(f"Arquivo: **{nome_img}**")
            if melhor_img: st.image(melhor_img, width=200)

st.title("Meu App de Reconhecimento")
# ...
