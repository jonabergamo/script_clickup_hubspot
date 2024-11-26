import requests
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from tqdm import tqdm  # Biblioteca para barra de progresso

# Carregar variáveis de ambiente
load_dotenv()

api_key = os.getenv('API_KEY')
column_name = os.getenv('COLUMN_ID_NAME', 'task_id')
file_name = os.getenv('FILE_NAME', 'tasks.xlsx')
sleep_time = float(os.getenv('SLEEP_TIME', 0.2))

headers = {
    "Authorization": api_key
}

df_tasks = pd.read_excel(file_name)
df_tasks[column_name] = df_tasks[column_name].astype(str)
task_ids = df_tasks[column_name].tolist()
total_tasks = len(task_ids)

comments_data = []

# Processar cada task_id com barra de progresso
with tqdm(total=total_tasks, desc="Processing Comments", unit="task", leave=False) as pbar:
    for task_id in task_ids:
        url_comments = f"https://api.clickup.com/api/v2/task/{task_id}/comment"
        response = requests.get(url_comments, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            comments = data.get('comments', [])
            
            for comment in comments:
                comment_id = comment.get('id', '')
                comment_text = comment.get('comment_text', '')
                date = comment.get('date', '')
                resolved = comment.get('resolved', False)
                
                user = comment.get('user', {})
                user_id = user.get('id', '')
                username = user.get('username', '')
                user_email = user.get('email', '')
                
                if date:
                    date = datetime.fromtimestamp(int(date) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date = ''
                
                attachments = comment.get('attachments', [])
                attachment_urls = [attachment.get('url', '') for attachment in attachments]
                attachment_urls_str = ', '.join(attachment_urls)
                
                reactions = comment.get('reactions', [])
                reaction_emojis = [reaction.get('reaction', '') for reaction in reactions]
                reactions_str = ', '.join(reaction_emojis)
                
                assignees = comment.get('assignees', [])
                assignee_ids = [assignee.get('id', '') for assignee in assignees]
                assignee_ids_str = ', '.join(assignee_ids)

                comment_data = {
                    column_name: task_id,
                    'Comment ID': comment_id,
                    'Comment Text': comment_text,
                    'Date': date,
                    'Resolved': resolved,
                    'User ID': user_id,
                    'Username': username,
                    'User Email': user_email,
                    'Attachment URLs': attachment_urls_str,
                    'Reactions': reactions_str,
                    'Assignee IDs': assignee_ids_str
                }
                
                comments_data.append(comment_data)
        else:
            tqdm.write(f"Erro ao buscar comentários da tarefa {task_id}: {response.status_code}")
        
        # Atualizar a barra de progresso
        pbar.update(1)
        time.sleep(sleep_time)

# Criar diretório de saída
output_folder = 'out'
os.makedirs(output_folder, exist_ok=True)

now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_file = os.path.join(output_folder, f'comments-{now}.csv')

comments_df = pd.DataFrame(comments_data)
comments_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Comentários exportados para '{output_file}'")
