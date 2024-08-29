import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.operators.bash import BashOperator
import pandas as pd

# Data transformation function
def transform_data(ti):
    consolidated_file = ti.xcom_pull(task_ids='consolidate_data')
    df = pd.read_csv(consolidated_file)
    
    # Realizar transformações nos dados
    df = df.drop_duplicates()
    df = df.fillna(method='ffill')

    transformed_file = '/Documents/transformed_data.csv'
    df.to_csv(transformed_file, index=False)
    ti.xcom_push(key='transformed_data_file', value=transformed_file)
    return transformed_file

# Data consolidation function
def consolidate_data(ti):
    # Exemplo de caminhos para os arquivos
    csv_file = '/Documents/dado_csv.txt'
    tsv_file = '/Documents/dado_tsv.txt'
    fixed_width_file = '/Documents/dado.txt'
    
    # Ler dados dos arquivos
    df_csv = pd.read_csv(csv_file)
    df_tsv = pd.read_csv(tsv_file, sep='\t')
    df_fixed_width = pd.read_fwf(fixed_width_file)
    
    # Consolidar dados
    consolidated_df = pd.concat([df_csv, df_tsv, df_fixed_width], ignore_index=True)
    consolidated_file = '/Documents/consolidated_data.csv'
    consolidated_df.to_csv(consolidated_file, index=False)
    ti.xcom_push(key='consolidated_data_file', value=consolidated_file)
    return consolidated_file


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1
}

# Define the DAG
with DAG(
    dag_id='dagCursea',
    start_date=datetime(2024, 7, 19),
    schedule_interval='30 * * * *',  # Runs every 30 minutes
    catchup=False,  # Don't run for past missed intervals
) as dag:
    
    # Task 2.1: Create a task to unzip data. (2 pts)
    unzip_task = BashOperator(
        task_id='unzip_data',
        bash_command='unzip -u /Documents/dado.zip -d /Documents'
    )

    # Task 2.2: Create a task to extract data from csv file (2 pts)
    extract_csv_task = BashOperator(
        task_id='extract_csv_data',
        bash_command='cut -d "," -f 2,3 /Documents/seudado.csv > /Documents/dado_csv.txt'
    )
     
    # Task 2.3: Create a task to extract data from tsv file (2 pts)
    extract_tsv_task = BashOperator(
        task_id='extract_tsv_data',
        bash_command='cut -f 2,4 /Documents/seudado.tsv > /Documents/dado_tsv.txt'
    )
      
    # Task 2.4: Create a task to extract data from fixed width file (2 pts) 
    extract_fixed_width_task = BashOperator(
        task_id='extract_fixed_width_data',
        bash_command='cut -c 1-10,21-30 /Documents/seudado.txt > /Documents/dado.txt'
    )

    # Task 2.5: Create a task to consolidate data extracted from previous tasks (2 pts)
    consolidate_task = PythonOperator(
        task_id='consolidate_data',
        python_callable=consolidate_data
    )

    # Task 2.6: Transform the data (2 pts)
    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    # Task 2.7: Define the task pipeline (1 pt)
    unzip_task >> [extract_csv_task, extract_tsv_task, extract_fixed_width_task]
    extract_csv_task >> consolidate_task
    extract_tsv_task >> consolidate_task
    extract_fixed_width_task >> consolidate_task
    consolidate_task >> transform_task
