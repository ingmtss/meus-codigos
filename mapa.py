import os
import pandas as pd
import folium
from folium import CustomIcon
from PIL import Image

# Caminho do arquivo Excel
file_path = "Locais - Manaus.xlsx"

# Carregar os dados do arquivo Excel
dataset = pd.read_excel(file_path)

# Verificar as primeiras linhas do DataFrame para garantir que as colunas estejam corretas
print(dataset.head())

# Substituir vírgulas por ponto e garantir que latitude e longitude sejam do tipo float
dataset['LONGITUDE'] = dataset['LONGITUDE'].replace(',', '.', regex=True).astype(float)
dataset['LATITUDE'] = dataset['LATITUDE'].replace(',', '.', regex=True).astype(float)

# Função para retornar o caminho local do ícone PNG baseado na legenda
def get_icon_path(legenda):
    icon_paths = {
        'Ponto Turístico': "ponto_turistico.png",
        'Hospital': "hospital.png",
        'Restaurante': "restaurante.png",
        'Local do Evento': "local_evento.png",
        'Sede da Defesa Civil': "defesa.png",
        'Hotel': "hotel.png"
    }
    
    # Retorna o caminho para o ícone, ou um ícone padrão se não encontrar
    return icon_paths.get(legenda, "icons/default.png")

# Criar o mapa com o tema CartoDB VoyagerLabelsUnder
mapa = folium.Map(
    location=[dataset['LATITUDE'].mean(), dataset['LONGITUDE'].mean()],
    zoom_start=12,
    tiles='CartoDB.VoyagerLabelsUnder'  # Tema CartoDB VoyagerLabelsUnder
)

# Adicionar marcadores com ícones personalizados ao mapa
for idx, row in dataset.iterrows():
    legenda = row['Legenda']  # Coluna que contém o tipo do local
    icon_path = get_icon_path(legenda)  # Obtém o caminho do ícone

    # Verifica se o caminho do ícone é válido
    if os.path.exists(icon_path):
        try:
            # Carregar a imagem do ícone usando PIL (Pillow)
            icon_image = Image.open(icon_path)
            icon_image = icon_image.convert("RGBA")  # Converte para RGBA para garantir a transparência
            
            # Salvar a imagem temporariamente com a extensão correta para folium
            temp_icon_path = "temp_icon.png"
            icon_image.save(temp_icon_path, "PNG")

            # Usando o CustomIcon do folium com uma imagem local (PNG)
            icon = CustomIcon(
                icon_image=temp_icon_path,
                icon_size=(25, 25),  # Ajuste o tamanho do ícone
                icon_anchor=(15, 30),  # Ancoragem do ícone
                popup_anchor=(0, -30)  # Ajuste do popup
            )

            # Criar o conteúdo do popup com descrição e foto
            descricao = row['description'] if 'description' in row else "Descrição não disponível"
            photo_url = row['foto'] if 'foto' in row else None  # Coluna 'Foto' contendo o caminho da imagem

            # Construção do HTML para o popup
            popup_content = f"""
            <b>{row['name']}</b><br>
            <p>{descricao}</p>
            """
            if photo_url:
                # Se houver uma foto, exibe a imagem no popup
                popup_content += f'<img src="{photo_url}" alt="Foto do Local" style="width:100%; height:auto;">'
            
            folium.Marker(
                location=[row['LATITUDE'], row['LONGITUDE']], 
                icon=icon, 
                popup=folium.Popup(popup_content, max_width=300)  # Exibe o popup com conteúdo HTML
            ).add_to(mapa)

        except Exception as e:
            print(f"Erro ao carregar o ícone para {row['name']}: {e}")
    else:
        print(f"Ícone não encontrado para {legenda}: {icon_path}")

# Salvar o mapa como um arquivo HTML
mapa.save('mapa_icons_local.html')

# Exibir mensagem para indicar que o mapa foi gerado com sucesso
print("Mapa HTML com ícones personalizados gerado com sucesso.")
