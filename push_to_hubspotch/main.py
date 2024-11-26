import pandas as pd
import os
from dotenv import load_dotenv
import requests
from tqdm import tqdm
import time  # Para adicionar tempo de espera entre requisições

# Carregar variáveis de ambiente
load_dotenv()

hubspot_api_key = os.getenv('HUBSPOT_API_KEY')
hubspot_headers = {
    "Authorization": f"Bearer {hubspot_api_key}",
    "Content-Type": "application/json"
}

input_tasks_file = os.getenv('TASKS_FILE', 'in/tasks.csv')
input_users_file = os.getenv('USERS_FILE', 'in/users.xlsx')
input_comments_file = os.getenv('COMMENTS_FILE', 'in/comments.csv')
sleep_time = float(os.getenv('SLEEP_TIME', 0.2))

# Carregar arquivos
df_tasks = pd.read_csv(input_tasks_file)
df_users = pd.read_excel(input_users_file)
df_comments = pd.read_csv(input_comments_file)

# Mapear emails para IDs de usuários
email_to_user_id = dict(zip(df_users['Email'], df_users['User ID']))

# Parâmetro opcional para definir o limite de tarefas
limit_tasks = 1  # Altere para limitar o número de tarefas

# Processar tarefas com barra de progresso detalhada
total_tasks = len(df_tasks)
tasks_to_process = df_tasks.iloc[:limit_tasks] if limit_tasks else df_tasks


# Função para criar uma nota em uma tarefa no HubSpot
def create_hubspot_note(hubspot_id, comment, timestamp, user_id):
    """
    Cria uma nota em uma tarefa no HubSpot, associada a um usuário.
    """
    url = f"https://api.hubapi.com/engagements/v1/engagements"
    data = {
        "engagement": {
            "active": True,
            "type": "NOTE",
            "timestamp": timestamp,
            "ownerId": user_id  # Relaciona a nota ao criador
        },
        "associations": {
            "ticketIds": [hubspot_id],  # Associa ao Hubspot ID
        },
        "metadata": {
            "body": comment
        }
    }
    response = requests.post(url, headers=hubspot_headers, json=data)
    return response

# Processamento principal
with tqdm(total=len(tasks_to_process), desc="Processing Tasks", unit="task") as tasks_pbar:
    for _, row in tasks_to_process.iterrows():
        hubspot_id = row.get('Hubspot ID', '')
        task_id = row.get('Task ID', '')
        email = str(row.get('E-mail', '')).strip() if pd.notnull(row.get('E-mail')) else None
        attachments = row.get('Attachment Links', '')

        # Atualizar a barra para exibir o Task ID em processamento
        tasks_pbar.set_description(f"Processing Task ID {task_id}")

        # Verificar se o email do criador é válido e obter o ID do usuário
        user_id = email_to_user_id.get(email, None)

        # Processar comentários associados à tarefa com barra de progresso separada
        task_comments = df_comments[df_comments['ID Clickup'] == task_id]

        with tqdm(total=len(task_comments), desc=f"Processing Comments for Task {task_id}", unit="comment", leave=True) as comments_pbar:
            for _, comment_row in task_comments.iterrows():
                comment_text = comment_row.get('Comment Text', '')
                comment_date = comment_row.get('Date', '')
                comment_user_email = comment_row.get('User Email', '')
                comment_user_id = email_to_user_id.get(comment_user_email, None)

                # Validar se o usuário foi encontrado antes de criar a nota
                if comment_user_id is None:
                    tqdm.write(f"User ID not found for email: {comment_user_email}. Skipping comment.")
                    comments_pbar.update(1)
                    continue

                # Processar data do comentário
                try:
                    comment_timestamp = int(pd.to_datetime(comment_date).timestamp() * 1000)
                except ValueError:
                    comments_pbar.update(1)
                    continue

                # Criar a nota para o comentário
                response = create_hubspot_note(hubspot_id, comment_text, comment_timestamp, comment_user_id)

                if response.status_code != 201:
                    tqdm.write(f"Erro ao criar nota para Task ID {task_id}: {response.status_code}, {response.text}")

                comments_pbar.update(1)

        tasks_pbar.update(1)

tqdm.write("All tasks and comments processed and pushed to HubSpot.")
