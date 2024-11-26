import requests
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from tqdm import tqdm  # Biblioteca para barra de progresso

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
api_key = os.getenv('API_KEY')
column_name = os.getenv('COLUMN_ID_NAME', 'task_id')
hubspot_column_name = os.getenv('HUBSPOT_COLUMN_NAME', 'Hubspot ID')  # Nome da coluna do Hubspot ID
file_name = os.getenv('FILE_NAME', 'tasks.xlsx')
sleep_time = float(os.getenv('SLEEP_TIME', 0.2))

headers = {
    "Authorization": api_key
}

# Carregar os IDs das tarefas do arquivo Excel
df_tasks = pd.read_excel(file_name)
df_tasks[column_name] = df_tasks[column_name].astype(str)
df_tasks[hubspot_column_name] = df_tasks[hubspot_column_name].astype(str)  # Garantir que Hubspot ID seja string
task_ids = df_tasks[column_name].tolist()
hubspot_ids = df_tasks[hubspot_column_name].tolist()  # Obter os Hubspot IDs correspondentes
total_tasks = len(task_ids)

tasks_data = []

# Processar cada task_id com barra de progresso
with tqdm(total=total_tasks, desc="Processing Tasks", unit="task", leave=False) as pbar:
    for task_id, hubspot_id in zip(task_ids, hubspot_ids):  # Processar task_id e hubspot_id juntos
        url_task = f"https://api.clickup.com/api/v2/task/{task_id}"
        response = requests.get(url_task, headers=headers)

        if response.status_code == 200:
            task = response.json()

            # Custom Fields Parsing
            custom_fields = {}
            for field in task.get('custom_fields', []):
                custom_fields[field['name']] = field.get('value', '')

            # Extrair links dos attachments
            attachments = task.get('attachments', [])
            attachment_links = ', '.join([attachment.get('url', '') for attachment in attachments])

            task_data = {
                'Hubspot ID': hubspot_id,  # Inclui o Hubspot ID
                'Task ID': task.get('id', ''),
                'Name': task.get('name', ''),
                'Text Content': task.get('text_content', ''),
                'Description': task.get('description', ''),
                'Status': task.get('status', {}).get('status', ''),
                'Priority': task.get('priority', {}).get('priority', '') if task.get('priority') else '',
                'Due Date': task.get('due_date', ''),
                'Start Date': task.get('start_date', ''),
                'Date Created': task.get('date_created', ''),
                'Date Updated': task.get('date_updated', ''),
                'Creator Username': task.get('creator', {}).get('username', ''),
                'Assignees': ', '.join([assignee.get('username', '') for assignee in task.get('assignees', [])]),
                'Tags': ', '.join([tag.get('name', '') for tag in task.get('tags', [])]),
                'Attachment Links': attachment_links,
                'URL': task.get('url', '')
            }

            # Adicionar campos personalizados
            task_data.update(custom_fields)

            # Converter datas para formato legível
            for date_field in ['Due Date', 'Start Date', 'Date Created', 'Date Updated']:
                if task_data[date_field]:
                    task_data[date_field] = datetime.fromtimestamp(int(task_data[date_field]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    task_data[date_field] = ''

            tasks_data.append(task_data)
        else:
            tqdm.write(f"Erro ao buscar informações da tarefa {task_id}: {response.status_code}")

        # Atualizar a barra de progresso
        pbar.update(1)
        time.sleep(sleep_time)

# Criar diretório de saída
output_folder = 'out'
os.makedirs(output_folder, exist_ok=True)

# Exportar para arquivo CSV
now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_file = os.path.join(output_folder, f'tasks-{now}.csv')

tasks_df = pd.DataFrame(tasks_data)
tasks_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Informações das tarefas exportadas para '{output_file}'")
