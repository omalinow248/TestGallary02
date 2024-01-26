import streamlit as st
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import os
from io import BytesIO

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Funkcja do łączenia z kontem Blob Storage
def connect_to_azure_storage():
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    return blob_service_client

# Funkcja do pobierania listy plików z Blob Storage
def list_files(container_name, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()
    for blob in blobs_list:
        st.write(f"- {blob.name}")
    return blobs_list

# Funkcja do dodawania nowego pliku
def add_new_file(blob_service_client, container_name):
    st.header("Dodaj nowy plik:")
    uploaded_file = st.file_uploader("Wybierz plik", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        st.write("Nazwa pliku:", uploaded_file.name)
        if st.button("Załaduj"):
            file_contents = uploaded_file.read()
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(uploaded_file.name)
            blob_client.upload_blob(file_contents, overwrite=True)
            st.success("Plik został załadowany!")

# Funkcja do pobierania pliku
def download_file(container_name, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()

    selected_file = st.selectbox("Wybierz plik do pobrania:",
                                 [blob.name for blob in blobs_list])
    if st.button("Pobierz"):
        blob_client = container_client.get_blob_client(selected_file)
        stream = BytesIO()
        blob_client.download_blob().download_to_stream(stream)
        st.download_button(label="Pobierz plik", data=stream.getvalue(), file_name=selected_file)
        
# Funkcja do usuwania plików
def delete_file(container_name, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()

    selected_file = st.selectbox("Wybierz plik do usunięcia:",
                                 [blob.name for blob in blobs_list])
    if st.button("Usuń"):
        blob_client = container_client.get_blob_client(selected_file)
        blob_client.delete_blob()
        st.success(f"Plik {selected_file} został usunięty!")
        st.experimental_rerun()

# Funkcja do obsługi interfejsu aplikacji Streamlit
def main():
    blob_service_client = connect_to_azure_storage()
    container_name = os.getenv("CONTAINER_NAME") 
    st.title("System do archiwizacji dokumentów")
    add_new_file(blob_service_client, container_name)
    st.header("Lista plików:")
    list_files(container_name, blob_service_client)
    st.header("Pobierz plik:")
    download_file(container_name, blob_service_client)
    st.header("Usuń plik:")
    delete_file(container_name, blob_service_client)

if __name__ == "__main__":
    main()
