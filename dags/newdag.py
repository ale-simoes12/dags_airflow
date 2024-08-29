from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime
from airflow.operators.bash import BashOperator
import pandas as pd
import json 
import requests

# Função que será executada pela DAG
def captura_conta_dados():
    url = "https://my-json-server.typicode.com/maujor/livros-json/livros"
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    qtd = len(df.index)
    return qtd


def branch_function(ti):
    qtd = ti.xcom_pull(task_ids='captura_conta_dados')
    if qtd >= 2:
        return 'valido'
    return 'nvalido'

# Definição da DAG
with DAG(
    'newdag',
    start_date=datetime(2024, 7, 19),
    schedule_interval='30 * * * *',
    catchup=False
) as dag:
    
    captura_conta_dados = PythonOperator(
        task_id='captura_conta_dados',
        python_callable=captura_conta_dados,
    )

    branch_task = BranchPythonOperator(
        task_id='e_valida',
        python_callable=branch_function,
    )

    valido = BashOperator(
        task_id='valido',
        bash_command="echo 'Quantidade OK'"
    )

    nvalido = BashOperator(
        task_id='nvalido',
        bash_command="echo 'Quantidade não OK'"
    )

captura_conta_dados >> branch_task >> [valido, nvalido]
