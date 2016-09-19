#----------------------------------------------------------------------------------
# Microsoft Developer & Platform Evangelism
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
#----------------------------------------------------------------------------------
# The example companies, organizations, products, domain names,
# e-mail addresses, logos, people, places, and events depicted
# herein are fictitious.  No association with any real company,
# organization, product, domain name, email address, logo, person,
# places, or events is intended or should be inferred.
#----------------------------------------------------------------------------------

import os
import config
from random_data import RandomData
from azure.storage import CloudStorageAccount
from azure.storage.blob import BlockBlobService, PageBlobService, AppendBlobService

#
# Azure Storage Blob Sample - Demonstrate how to use the Blob Storage service. 
# Blob storage stores unstructured data such as text, binary data, documents or media files. 
# Blobs can be accessed from anywhere in the world via HTTP or HTTPS. 
#
 
# Documentation References: 
#  - What is a Storage Account - http://azure.microsoft.com/en-us/documentation/articles/storage-whatis-account/ 
#  - Getting Started with Blobs - https://azure.microsoft.com/en-us/documentation/articles/storage-python-how-to-use-blob-storage/
#  - Blob Service Concepts - http://msdn.microsoft.com/en-us/library/dd179376.aspx 
#  - Blob Service REST API - http://msdn.microsoft.com/en-us/library/dd135733.aspx 
#  - Blob Service Python API - http://azure.github.io/azure-storage-python/ref/azure.storage.blob.html
#  - Storage Emulator - http://azure.microsoft.com/en-us/documentation/articles/storage-use-emulator/ 
#
 
class BlobBasicSamples():

    def __init__(self):
        self.random_data = RandomData()
    # Runs all samples for Azure Storage Blob service.
    # Input Arguments:
    # account - CloudStorageAccount to use for running the samples
    def run_all_samples(self, account):
        print('\n\nAzure Storage Blob sample - Starting.')
        
        try:
            # Block blob basics
            print('\n\n* Basic block blob operations *\n')
            self.basic_blockblob_operations(account)
            
            # Page blob basics
            print('\n\n* Basic page blob operations *\n')
            self.basic_pageblob_operations(account)
            
            if (config.IS_EMULATED == False):
                # Append blob basics
                # Append blob is not yet supported in the Emulator
                print('\n\n* Basic append blob operations *\n')
                self.basic_appendblob_operations(account)
            
        except Exception as e:
            if (config.IS_EMULATED):
                print('Error occurred in the sample. If you are using the emulator, please make sure the emulator is running.', e)
            else: 
                print('Error occurred in the sample. Please make sure the account name and key are correct.', e)

        finally:
            print('\nAzure Storage Blob sample - Completed.\n')
            
    
    # Runs basic block blob samples for Azure Storage Blob service.
    # Input Arguments:
    # container_name - Container name to use for running the samples
    def basic_blockblob_operations(self, account):
        blob_name1 = "blob1"
        blob_name2 = "blob2"
        file_to_upload = "HelloWorld.png"
        
        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()
        #blockblob_service = BlockBlobService(account_name=config.STORAGE_ACCOUNT_NAME, account_key=config.STORAGE_ACCOUNT_KEY)
        container_name = 'blockblobbasicscontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)
                    
            # Create blobs
            print('2. Create blobs')
            # Get full path on drive to file_to_upload by joining the fully qualified directory name and file name on the local drive
            full_path_to_file = os.path.join(os.path.dirname(__file__), file_to_upload)
            blockblob_service.create_blob_from_path(container_name, blob_name1, full_path_to_file)
            # Create blob from text
            blockblob_service.create_blob_from_text(container_name, blob_name2, self.random_data.get_random_name(256))
            
            # List all the blobs in the container 
            print('3. List Blobs in Container')
            generator = blockblob_service.list_blobs(container_name)
            for blob in generator:
                print('\tBlob Name: ' + blob.name)
            
            # Download the blob
            print('4. Download the blob');
            blockblob_service.get_blob_to_path(container_name, blob_name1, os.path.join(os.path.dirname(__file__), file_to_upload + '.copy.png'))
            blockblob_service.get_blob_to_path(container_name, blob_name2, os.path.join(os.path.dirname(__file__), 'blob2.copy.txt'))
            
            # Delete the blobs, this can be ommited because the container is deleted
            print('5. Delete blobs')
            blockblob_service.delete_blob(container_name, blob_name1)
            blockblob_service.delete_blob(container_name, blob_name2)
        finally:            
            # Delete the container
            print("6. Delete Container")
            if blockblob_service.exists(container_name):
                blockblob_service.delete_container(container_name)
        
    # Runs basic page blob samples for Azure Storage Blob service.
    # Input Arguments:
    # account - CloudStorageAccount to use for running the samples
    def basic_pageblob_operations(self, account):
        file_to_upload = "HelloPageBlobWorld.txt"
        
        # Create a block blob service object
        pageblob_service = account.create_page_blob_service()
        container_name = 'pageblobbasicscontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            pageblob_service.create_container(container_name)
                    
            # Create a page blob
            print('2. Creating Page Blob')
            pageblob_service.create_blob_from_bytes(container_name, file_to_upload, self.random_data.get_random_bytes(512))
            
            # List all the blobs in the container 
            print('3. List Blobs in Container')
            blob_list = pageblob_service.list_blobs(container_name)
            for blob in blob_list:
                print('\tBlob Name: ' + blob.name)
                
            # Read a page blob
            print('4. Reading a Page Blob')
            readblob = pageblob_service.get_blob_to_bytes(container_name, # name of the container
                                                        file_to_upload, # name of blob to read
                                                        start_range=3,  # page to start reading from
                                                        end_range=10)   # page to stop reading at
                    
            # Delete the blob, this can be ommited because the container is deleted
            print('5. Delete Page Blob')
            pageblob_service.delete_blob(container_name, file_to_upload)
        finally: 
            # Delete the container
            print("6. Delete Container")
            if pageblob_service.exists(container_name):
                pageblob_service.delete_container(container_name)

     
    # Runs basic append blob samples for Azure Storage Blob service.
    # Input Arguments:
    # container_name - Container name to use for running the samples
    def basic_appendblob_operations(self, account):
        file_to_upload = "HelloAppendBlobWorld.txt"
        
        # Create an append blob service object
        appendblob_service = account.create_append_blob_service()
        container_name = 'appendblobbasicscontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            appendblob_service.create_container(container_name)
                    
            # Create an append blob
            print('2. Create Append Blob')
            appendblob_service.create_blob(container_name, file_to_upload)
            
            # Write to an append blob
            print('3. Write to Append Blob')
            appendblob_service.append_blob_from_text(container_name, file_to_upload, '\tHello Append Blob world!\n')
            appendblob_service.append_blob_from_text(container_name, file_to_upload, '\tHello Again Append Blob world!')
                    
            # List all the blobs in the container 
            print('4. List Blobs in Container')
            generator = appendblob_service.list_blobs(container_name)
            for blob in generator:
                print('\tBlob Name: ' + blob.name)
            
            # Read the blob
            print('5. Read Append blob');
            append_blob = appendblob_service.get_blob_to_text(container_name, file_to_upload)
            print(append_blob.content)
            
            # Delete the blob, this can be ommited because the container is deleted
            print('6. Delete Append Blob')
            appendblob_service.delete_blob(container_name, file_to_upload)
        finally:            
            # Delete the container
            print("7. Delete Container")
            if appendblob_service.exists(container_name):
                appendblob_service.delete_container(container_name)