import pandas as pd
import folium

# Caminho do arquivo Excel
file_path = "C:/Users/ingri/OneDrive/Documentos/mapa/Principais Pontos Turísticos de Manaus- Principais Pontos Turísticos de Manaus.xlsx"

# Carregar os dados do arquivo Excel
dataset = pd.read_excel(file_path)

# Verificar as primeiras linhas do DataFrame para garantir que as colunas estejam corretas
print(dataset.head())

# Substituir vírgulas por ponto e garantir que latitude e longitude sejam do tipo float
# Convertendo para float para garantir que o Python entenda como números decimais
dataset['LATITUDE'] = dataset['LATITUDE'].replace(',', '.', regex=True).astype(float)
dataset['LONGITUDE'] = dataset['LONGITUDE'].replace(',', '.', regex=True).astype(float)

# Certifique-se de que as colunas corretas existem
dataset = dataset[['LATITUDE', 'LONGITUDE', 'name']]  # Ajuste 'name' conforme necessário

# Criar o mapa centralizado na média das coordenadas
mapa = folium.Map(location=[dataset['LATITUDE'].mean(), dataset['LONGITUDE'].mean()], zoom_start=12)

# Adicionar marcadores ao mapa
for idx, row in dataset.iterrows():
    folium.Marker([row['LATITUDE'], row['LONGITUDE']], popup=str(row['name'])).add_to(mapa)  # Convertendo para string

# Salvar o mapa como um arquivo HTML
mapa.save('mapa.html')

# Exibir mensagem para indicar que o mapa foi gerado com sucesso
print("Mapa HTML gerado com sucesso.")
