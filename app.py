import streamlit as st
from pymongo import MongoClient
from PIL import Image
import io
import gridfs

import streamlit as st
import os
import gridfs
from pymongo import MongoClient
from PIL import Image
import io

# --- 1. Configuração da Página ---
st.set_page_config(page_title="Galeria MongoDB", layout="wide")

st.title("📸 Gerenciador de Imagens - MongoDB Atlas")

# --- 2. Conexão com o Banco de Dados (Cacheada) ---
@st.cache_resource
def get_database_connection():
    # Substitua pela sua URI correta se necessário
    uri = "mongodb+srv://diegorlima8_db_user:04KskmDzmVNDK53t@cluster0.4nsgcvo.mongodb.net/?appName=Cluster0"
    client = MongoClient(uri)
    return client

try:
    client = get_database_connection()
    db = client['midias']
    fs = gridfs.GridFS(db)
    st.sidebar.success("Conectado ao MongoDB Atlas!")
except Exception as e:
    st.error(f"Erro ao conectar no banco: {e}")
    st.stop()

# --- 3. Seção de UPLOAD (Protegida por Botão) ---
st.header("1. Upload de Imagens")
st.markdown("Clique no botão abaixo para varrer a pasta local e salvar as imagens novas no banco.")

if st.button("Inciar Carregamento das Imagens"):
    pasta_imagens = 'frontalimages_manuallyaligned_part1'
    
    if os.path.exists(pasta_imagens):
        arquivos = [f for f in os.listdir(pasta_imagens) if f.lower().endswith('.jpg')]
        st.info(f"Encontrados {len(arquivos)} arquivos na pasta '{pasta_imagens}'. Processando...")
        
        barra_progresso = st.progress(0)
        contador = 0
        
        for i, nome_arquivo in enumerate(arquivos):
            caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
            
            # Verifica se já existe para não duplicar
            if not fs.exists({"filename": nome_arquivo}):
                try:
                    with open(caminho_completo, 'rb') as f:
                        fs.put(f, filename=nome_arquivo)
                        contador += 1
                except Exception as e:
                    st.error(f"Erro ao salvar {nome_arquivo}: {e}")
            
            # Atualiza barra de progresso
            barra_progresso.progress((i + 1) / len(arquivos))
            
        st.success(f"Processo finalizado! {contador} novas imagens foram salvas.")
    else:
        st.error(f"A pasta '{pasta_imagens}' não foi encontrada no diretório do projeto.")

st.divider()

# --- 4. Seção de GALERIA (Exibição) ---
st.header("2. Galeria de Imagens no Banco")

# Botão para atualizar a lista manualmente
if st.button("Atualizar Galeria"):
    st.rerun()

arquivos_banco = list(fs.find())
total_arquivos = len(arquivos_banco)

st.write(f"**Total de imagens no banco:** {total_arquivos}")

if total_arquivos > 0:
    # Cria colunas para exibir em grade (grid)
    cols = st.columns(4) # 4 imagens por linha
    
    # Limita a exibição para não travar se tiverem milhares (ex: mostra as últimas 20)
    # Remova o [:20] se quiser ver todas
    for index, arquivo in enumerate(arquivos_banco[:20]):
        coluna_atual = cols[index % 4]
        
        with coluna_atual:
            try:
                img_data = arquivo.read()
                image = Image.open(io.BytesIO(img_data))
                st.image(image, caption=arquivo.filename, use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao abrir {arquivo.filename}")
    
    if total_arquivos > 20:
        st.info("Exibindo apenas as primeiras 20 imagens para otimizar a performance.")
else:
    st.warning("Nenhuma imagem encontrada no GridFS.")

st.title("Meu App de Reconhecimento")
# ...
