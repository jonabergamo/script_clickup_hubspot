import requests
import pandas as pd
import os
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
api_key = os.getenv('HUBSPOT_API_KEY')
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
output_folder = 'out'
sleep_time = 0.2  # Pausa entre as requisições (ajuste conforme necessário)

# Função para buscar os owners da API do HubSpot
def get_hubspot_owners():
    url = "https://api.hubapi.com/crm/v3/owners"
    params = {"limit": 100}  # Ajuste conforme necessário
    all_owners = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            all_owners.extend(data.get('results', []))
            # Verifica se há uma próxima página
            paging = data.get('paging', {})
            url = paging.get('next', {}).get('link', None)
        else:
            print(f"Erro ao buscar owners: {response.status_code} - {response.text}")
            break
    return all_owners

# Buscar todos os owners
owners = get_hubspot_owners()

# Processar os dados dos owners
owners_data = []
for owner in owners:
    owner_data = {
        'ID': owner.get('id', ''),
        'Email': owner.get('email', ''),
        'Type': owner.get('type', ''),
        'First Name': owner.get('firstName', ''),
        'Last Name': owner.get('lastName', ''),
        'User ID': owner.get('userId', ''),
        'User ID (Including Inactive)': owner.get('userIdIncludingInactive', ''),
        'Created At': owner.get('createdAt', ''),
        'Updated At': owner.get('updatedAt', ''),
        'Archived': owner.get('archived', ''),
        'Teams': ', '.join([team.get('name', '') for team in owner.get('teams', [])])
    }
    owners_data.append(owner_data)

# Criar diretório de saída
os.makedirs(output_folder, exist_ok=True)

# Salvar os dados em um arquivo CSV
now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_file = os.path.join(output_folder, f'owners-{now}.csv')

owners_df = pd.DataFrame(owners_data)
owners_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Dados dos owners exportados para '{output_file}'")
