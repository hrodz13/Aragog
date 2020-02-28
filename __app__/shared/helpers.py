from . import env
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobClient, ContainerClient
import os
import logging

CREDENTIALS = ClientSecretCredential(env.TENANT_ID, env.CLIENT_ID, env.CLIENT_SECRET)

def retrieve_secret(secret_name):
    client = SecretClient(env.KEYVAULT_URI, CREDENTIALS)
    secret = client.get_secret(secret_name).value
    return secret

def download_blob(container_name, blob_name):
    blob = BlobClient(env.REPORTS_STGACCT_URI, container_name, blob_name, credential=CREDENTIALS)
    blob_data = blob.download_blob()
    return blob_data

def upload_blob(container_name, blob_name, blob_data):
    blob = BlobClient(env.REPORTS_STGACCT_URI, container_name, blob_name, credential=CREDENTIALS)
    response = blob.upload_blob(blob_data, overwrite=True)
    return response

def create_container(container_name):
    container = ContainerClient(env.REPORTS_STGACCT_URI, container_name, credential=CREDENTIALS)
    try:
        container.create_container()
    except Exception as e:
        logging.info(e)
