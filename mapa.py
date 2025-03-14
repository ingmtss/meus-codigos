import os
import pandas as pd
import folium
from folium import CustomIcon
from PIL import Image

# Caminho do arquivo Excel
file_path = "Locais - Manaus.xlsx"

# Carregar os dados do arquivo Excel
dataset = pd.read_excel(file_path)

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
        'Hotel': "hotel.png",
        'Aeroporto': "aeroporto.png"
    }
    
    # Retorna o caminho para o ícone, ou um ícone padrão se não encontrar
    return icon_paths.get(legenda, "icons/default.png")

# Criar o mapa com o tema CartoDB VoyagerLabelsUnder
mapa = folium.Map(
    location=[dataset['LATITUDE'].mean(), dataset['LONGITUDE'].mean()],
    zoom_start=12,
    tiles='CartoDB.VoyagerLabelsUnder'  # Tema CartoDB VoyagerLabelsUnder
)

# Armazenar os marcadores para adicionar ao painel
markers = []  # Lista para armazenar marcadores
marker_ids = []  # IDs dos marcadores para ligação com o JavaScript
marker_names = []  # Nomes dos pontos para mostrar na lateral

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
            descricao = row['Localização'] if 'Localização' in row else "Descrição não disponível"
            photo_url = row['foto'] if 'foto' in row else None  # Coluna 'Foto' contendo o caminho da imagem

            # Construção do HTML para o popup
            popup_content = f"""
            <b>{row['name']}</b><br>
            <p>{descricao}</p>
            """
            if photo_url:
                # Se houver uma foto, exibe a imagem no popup
                popup_content += f'<img src="{photo_url}" alt="Foto do Local" style="width:100%; height:auto;">'
            
            # Criar o marcador
            marker = folium.Marker(
                location=[row['LATITUDE'], row['LONGITUDE']], 
                icon=icon, 
                popup=folium.Popup(popup_content, max_width=300)  # Exibe o popup com conteúdo HTML
            )

            # Adiciona o marcador ao mapa
            marker.add_to(mapa)

            # Adiciona os detalhes do marcador para usar na caixa lateral
            marker_ids.append(f"marker_{idx}")
            markers.append(marker)
            marker_names.append(row['name'])

        except Exception as e:
            print(f"Erro ao carregar o ícone para {row['name']}: {e}")
    else:
        print(f"Ícone não encontrado para {legenda}: {icon_path}")

# Função para criar a caixa lateral com os pontos
def generate_sidebar(markers, marker_ids, marker_names):
    sidebar_content = """
    <div id="sidebar" style="width: 300px; height: 100%; position: absolute; top: 0; left: 0; background-color: #f8f9fa; box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); overflow-y: scroll; z-index: 9999; padding: 10px;">
        <h2 style="font-family: Arial, sans-serif; color: #007bff;">Pesquisa</h2>
        <input type="text" id="search" placeholder="Buscar por nome" style="width: 100%; padding: 8px; margin-bottom: 15px; border-radius: 4px; border: 1px solid #ccc; transition: 0.3s;">
        <ul id="points-list" style="list-style-type: none; padding-left: 10px;">
    """
    for idx, name in enumerate(marker_names):
        sidebar_content += f"""
        <li onclick="centerMap({markers[idx].location[0]}, {markers[idx].location[1]}, '{marker_ids[idx]}')"
            style="padding: 8px; margin-bottom: 5px; border-radius: 4px; cursor: pointer; transition: 0.3s; background-color: #f1f1f1;">
            <b>{name}</b>
        </li>
        """
    
    sidebar_content += """
        </ul>
    </div>
    <script>
        // Função para centralizar o mapa em um ponto e abrir o popup
        function centerMap(lat, lng, markerId) {
            map.setView([lat, lng], 14);  // Centraliza o mapa no ponto
            setTimeout(function() {
                var marker = map._layers[markerId];  // Obtém o marcador com o ID
                marker.openPopup();  // Abre o popup
            }, 500);  // Espera meio segundo para garantir que o mapa foi centralizado
        }

        // Filtra os pontos baseado no texto de busca
        document.getElementById('search').addEventListener('input', function() {
            let searchText = this.value.toLowerCase();
            let items = document.querySelectorAll('#points-list li');
            items.forEach(item => {
                let name = item.innerText.toLowerCase();
                if (name.includes(searchText)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    </script>
    """

    return sidebar_content

# Gerar o conteúdo da caixa lateral
sidebar_html = generate_sidebar(markers, marker_ids, marker_names)

# Adicionar o conteúdo da caixa lateral ao mapa
mapa.get_root().html.add_child(folium.Element(sidebar_html))

# Salvar o mapa como um arquivo HTML
mapa.save('mapa.html')

# Exibir mensagem para indicar que o mapa foi gerado com sucesso
print("Mapa HTML com ícones personalizados, caixa lateral e popups automáticos gerado com sucesso.")
