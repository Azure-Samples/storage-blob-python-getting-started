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
import base64
import datetime
import time
from azure.storage import CloudStorageAccount, AccessPolicy
from azure.storage.blob import BlockBlobService, PageBlobService, AppendBlobService
from azure.storage.models import CorsRule, Logging, Metrics, RetentionPolicy, ResourceTypes, AccountPermissions
from azure.storage.blob.models import BlobBlock, ContainerPermissions, ContentSettings
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
class BlobAdvancedSamples():

    def __init__(self):
        self.random_data = RandomData()

    # Runs all samples for Azure Storage Blob service.
    # Input Arguments:
    # account - CloudStorageAccount to use for running the samples
    def run_all_samples(self, account):
        print('\n\nAzure Storage Blob advanced sample - Starting.')
        
        try:
            print('\n\n* Container operations *\n')
            self.list_containers(account)

            print('\n\n* Set CORS *\n')
            self.set_cors_rules(account)

            print('\n\n* Container lease *\n')
            self.lease_container(account)

            print('\n\n* Copy blob *\n')
            self.copy_blob(account)
            
            print('\n\n* Page blob operations *\n')
            self.page_blob_operations(account)
            
            print('\n\n* Block blob operations *\n')
            self.block_blob_operations(account)

            print('\n\n* Properties and Metadata operations *\n')
            self.properties_and_metadata_operations(account)
            
            print('\n\n* Container ACL operations *\n')
            self.container_acl_operations(account)

            print('\n\n* Blob lease *\n')
            self.lease_blob(account)  
            
            if (config.IS_EMULATED):
                print('\nShared Access Signature is not supported in emulator');
            else:
                print('\n\n* Container with SAS operations *\n')
                self.container_operations_with_sas(account)      
  
                print('\n\n* SAS with access policy *\n')
                self.sas_with_container_access_policy(account)

                print('\n\n* Set blob service logging and metrics properties *\n')
                self.set_service_properties(account)

        except Exception as e:
            if (config.IS_EMULATED):
                print('Error occurred in the sample. If you are using the emulator, please make sure the emulator is running.', e)
            else: 
                print('Error occurred in the sample. Please make sure the account name and key are correct.', e)

        finally:
            print('\nAzure Storage Blob advanced sample - Completed.\n')


    # Copy a source blob to a destination blob
    def copy_blob(self, account):

        file_upload = "HelloWorld.png"
        container_name = 'blockblobcontainer' + self.random_data.get_random_name(6)

        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)
                    
            # Upload file as a block blob
            print('2. Upload BlockBlob')
            #Get full path on drive to file_to_upload by joining the fully qualified directory name and file name on the local drive
            full_path_to_file = os.path.join(os.path.dirname(__file__), file_upload)
            blockblob_service.create_blob_from_path(container_name, file_upload, full_path_to_file)

            target_blob = "target.png"
            blob_source_url = blockblob_service.make_blob_url(container_name, file_upload)

            print('3. Copy blob')
            blockblob_service.copy_blob(container_name, target_blob, blob_source_url)

            print('4. Get target blob')
            target_blob_properties = blockblob_service.get_blob_properties(container_name, target_blob)

            print('5. Get copy properties')
            copy_properties = target_blob_properties.properties.copy
            
            print('Copy properties status: ' + copy_properties.status)

            if(copy_properties.status == "pending"):
                print('6. Abort copy')
                blockblob_service.abort_copy_blob(container_name, blob_name, copy_properties.id)
        finally:
            # Delete the container
            print("7. Delete Container")
            if blockblob_service.exists(container_name):
                blockblob_service.delete_container(container_name)

    def sas_with_container_access_policy(self, account):
        container_name = 'demosasblobcontainer' + self.random_data.get_random_name(6)
        
        blockblob_service = account.create_block_blob_service()
        
        try:
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)
            
            print('2. Create blob "blo1" with text')
            blockblob_service.create_blob_from_text(container_name, 'blob1', b'hello world')

            print('3. Set access policy for container')
            # Set access policy on container
            access_policy = AccessPolicy(permission=ContainerPermissions.READ,
                                        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
            identifiers = {'id': access_policy}
            acl = blockblob_service.set_container_acl(container_name, identifiers)

            # Wait 30 seconds for acl to propagate
            print('Wait 30 seconds for acl to propagate')
            time.sleep(30)

            print('4. Get sas for access policy in container')
            # Indicates to use the access policy set on the container
            sas = blockblob_service.generate_container_shared_access_signature(
                container_name,
                id='id'
            )

            print('5. Create blob service with sas')
            # Create a service and use the SAS
            shared_blockblob_service = BlockBlobService(
                account_name=account.account_name,
                sas_token=sas,
            )

            print('6. Read blob content with sas')
            blob = shared_blockblob_service.get_blob_to_text(container_name, 'blob1')
            content = blob.content # hello world
        finally:
            print('7. Delete container')
            blockblob_service.delete_container(container_name)
        
        print("SAS with access policy sample completed")
        
    def container_operations_with_sas(self, account):
        container_name = 'demosasblobcontainer' + self.random_data.get_random_name(6)
        
        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()
        
        # Create a Shared Access Signature for the account
        print('1.Get account sas')
        
        account_sas = blockblob_service.generate_account_shared_access_signature(
            ResourceTypes.CONTAINER + ResourceTypes.OBJECT, 
            AccountPermissions.READ + AccountPermissions.WRITE + AccountPermissions.DELETE + AccountPermissions.LIST + AccountPermissions.CREATE, 
            datetime.datetime.utcnow() + datetime.timedelta(hours=1))

        shared_account = CloudStorageAccount(account_name=account.account_name, sas_token=account_sas)
        shared_account_block_service = shared_account.create_block_blob_service()

        try:
            print('2. Create container with account sas. Container name - ' + container_name)
            shared_account_block_service.create_container(container_name)
            
            # For the purposes of the demo, get a Container SAS
            # In a real-world application, the above Account SAS can be used
            print('3. Get container sas')
            container_sas = blockblob_service.generate_container_shared_access_signature(
                container_name, 
                ContainerPermissions.READ + ContainerPermissions.WRITE + ContainerPermissions.DELETE + ContainerPermissions.LIST, 
                datetime.datetime.utcnow() + datetime.timedelta(hours=1))
            
            shared_container_account = CloudStorageAccount(account_name=account.account_name, sas_token=container_sas)
            shared_container_block_service = shared_container_account.create_block_blob_service()
            
            print('4. Create blob with container sas')
            shared_container_block_service.create_blob_from_text(container_name, 'myblob', 'blob data')
            
            print('5. List blobs with container sas')
            blobs = shared_container_block_service.list_blobs(container_name)
            for blob in blobs:
                print('blob ' + blob.name)
            
            print('6. Delete blob with container sas')
            shared_container_block_service.delete_blob(container_name, 'myblob')
        finally:            
            print('7. Delete container')
            blockblob_service.delete_container(container_name)
            
        print("Containers Sas sample completed")
        
    def list_containers(self, account):
        
        container_prefix = 'blockblobcontainers' + self.random_data.get_random_name(6)
        
        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()

        try:
            # Create containers
            for i in range(5):
                container_name = container_prefix + str(i)
                print('1. Create a container with name - ' + container_name)
                blockblob_service.create_container(container_name)
            
            # List all the blobs in the container 
            print('2. List containers with prefix ' + container_prefix)
            containers = blockblob_service.list_containers(container_prefix)
            for container in containers:
                print('\tContainer Name: ' + container.name)
        finally:
            # Delete the containers
            print("3. Delete Containers")
            for i in range(5):
                container_name = container_prefix + str(i)
                if blockblob_service.exists(container_name):
                    blockblob_service.delete_container(container_name)
            
        print("Containers sample completed")

    def container_acl_operations(self, account):
        
        container_name = 'aclblockblobcontainer' + self.random_data.get_random_name(6)
        
        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()

        try:
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)
                
            print('2. Set access policy for container')
            access_policy = AccessPolicy(permission=ContainerPermissions.READ,
                                        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
            identifiers = {'id': access_policy}
            blockblob_service.set_container_acl(container_name, identifiers)

            print('3. Get access policy from container')
            acl = blockblob_service.get_container_acl(container_name)

            print('4. Clear access policy in container')
            # Clear
            blockblob_service.set_container_acl(container_name)

        finally:            
            print('5. Delete container')
            blockblob_service.delete_container(container_name)
            
        print("Container ACL operations sample completed")
        
    def properties_and_metadata_operations(self, account):
        file_blob_name = "HelloWorld.png"
        text_blob_name = "Text"
         
        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()

        container_name = 'blockblobbasicscontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name and custom metadata - ' + container_name)
            blockblob_service.create_container(container_name, {'sample':'azure-storage'})
                    
            # Upload file as a block blob
            print('2. Uploading BlockBlob from file with properties and custom metadata')
            #Get full path on drive to file_to_upload by joining the fully qualified directory name and file name on the local drive
            full_path_to_file = os.path.join(os.path.dirname(__file__), file_blob_name)
            
            blockblob_service.create_blob_from_path(container_name, file_blob_name, full_path_to_file, 
                content_settings=ContentSettings(content_type='application/png'),
                metadata={'category':'azure-samples'})
            
            blockblob_service.create_blob_from_text(container_name, text_blob_name, 'Data',
                content_settings=ContentSettings(content_encoding ='UTF-8', content_language='en'),
                metadata={'origin':'usa', 'title': 'azure-samples'})
            
            # Get all the container properties 
            print('3. Get Container metadata')

            container = blockblob_service.get_container_properties(container_name)
            
            print('    Metadata:')

            for key in container.metadata:
                print('        ' + key + ':' + container.metadata[key])
            
            # Get all the blob properties 
            print('4. Get Blob properties')
            blob = blockblob_service.get_blob_properties(container_name, file_blob_name)
            
            print('    Metadata:')
            for key in blob.metadata:
                print('        ' + key + ':' + blob.metadata[key])
            
            print('    Properties:')
            print('        Content-Type:' + blob.properties.content_settings.content_type)
        finally:            
            # Delete the container
            print("5. Delete Container")
            if blockblob_service.exists(container_name):
                blockblob_service.delete_container(container_name)
        
    # Set CORS
    def set_cors_rules(self, account):

        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()
        
        cors_rule = CorsRule(
            allowed_origins=['*'], 
            allowed_methods=['POST', 'GET'],
            allowed_headers=['*'],
            exposed_headers=['*'],
            max_age_in_seconds=3600)
        
        print('1. Get Cors Rules')
        original_cors_rules =  blockblob_service.get_blob_service_properties().cors;
        
        try:
            print('2. Overwrite Cors Rules')
            blockblob_service.set_blob_service_properties(cors=[cors_rule])
        finally:        
            print('3. Revert Cors Rules back the original ones')
            #reverting cors rules back to the original ones
            blockblob_service.set_blob_service_properties(cors=original_cors_rules)
        
        print("CORS sample completed")

    # Lease Container
    def lease_container(self, account):
        # Create a Block Blob Service object
        blockblob_service = account.create_block_blob_service()
        
        try:
            container_name = 'blockblobcontainer' + self.random_data.get_random_name(6)
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)

            print('2. Acquire lease on container')
            lease_id = blockblob_service.acquire_container_lease(container_name, lease_duration=15)

            print("3. Deleted container without lease")
            try:
                blockblob_service.delete_container(container_name)
            except:
                print('Got expected exception. Cannot delete container, lease not specified')
        finally:
            print("4. Delete container with lease")
            blockblob_service.delete_container(container_name, lease_id=lease_id)

        print("Lease container sample completed")

    # Lease Blob
    def lease_blob(self, account):
        blob_name = "exclusive"
        
        # Create an block blob service object
        blockblob_service = account.create_block_blob_service()
        container_name = 'blobcontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)
                    
            # Create a block blob
            print('2. Create Block Blob')
            blob = self.random_data.get_random_bytes(255)
            blockblob_service.create_blob_from_bytes(container_name, blob_name, blob)
            
            print('3. Acquire lease on blob')
            lease_id = blockblob_service.acquire_blob_lease(container_name, blob_name, lease_duration=15)
            
            # Write to a block blob
            print('4. Try to write to Block Blob without lease')
            block_id = self.random_data.get_random_name(32)
            block = self.random_data.get_random_bytes(255)
            try:
                blockblob_service.put_block(container_name, blob_name, block, block_id)
            except:
                print('Got expected exception. Cannot write blob, lease not specified')

            print('5. Write to Block Blob with lease')
            blockblob_service.put_block(container_name, blob_name, block, block_id, lease_id=lease_id)

            print("6. Deleted blob without lease")
            try:
                blockblob_service.delete_blob(container_name, blob_name)
            except:
                print('Got expected exception. Cannot delete blob, lease not specified')

            print("7. Delete blob with lease")
            blockblob_service.delete_blob(container_name, blob_name, lease_id=lease_id)
        finally:
            print("8. Delete container")
            if blockblob_service.exists(container_name):
                blockblob_service.delete_container(container_name)

        print("Lease blob sample completed")
        
    #Page Blob Operations
    def page_blob_operations(self, account):
        file_to_upload = "HelloWorld.png"
        page_size = 1024;
        
        # Create an page blob service object
        pageblob_service = account.create_page_blob_service()
        container_name = 'pageblobcontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            pageblob_service.create_container(container_name)
            
            # Create a new page blob to upload the file
            print('2. Create a page blob')
            pageblob_service.create_blob(container_name, file_to_upload, page_size * 1024)
            
            # Read the file
            print('3. Upload pages to page blob')
            index = 0
            with open(file_to_upload, "rb") as file:
                file_bytes = file.read(page_size)
                while len(file_bytes) > 0:
                    if len(file_bytes) < page_size:
                        file_bytes = bytes(file_bytes + bytearray(page_size - len(file_bytes)))
                        
                    pageblob_service.update_page(container_name, file_to_upload, file_bytes, index * page_size, index * page_size + page_size - 1)
                    
                    file_bytes = file.read(page_size)
                    
                    index = index + 1
            
            pages = pageblob_service.get_page_ranges(container_name, file_to_upload)
            
            print('4. Enumerate pages in page blob')
            for page in pages:
                print('Page ' + str(page.start) + ' - ' + str(page.end))
        finally:
            print('5. Delete container')
            if pageblob_service.exists(container_name):
                pageblob_service.delete_container(container_name)

    #Block Blob Operations
    def block_blob_operations(self, account):
        file_to_upload = "HelloWorld.png"
        block_size = 1024
        
        # Create an page blob service object
        blockblob_service = account.create_block_blob_service()
        container_name = 'blockblobcontainer' + self.random_data.get_random_name(6)

        try:
            # Create a new container
            print('1. Create a container with name - ' + container_name)
            blockblob_service.create_container(container_name)
            
            blocks = []
            
            # Read the file
            print('2. Upload file to block blob')
            with open(file_to_upload, "rb") as file:
                file_bytes = file.read(block_size)
                while len(file_bytes) > 0:
                    block_id = self.random_data.get_random_name(32) 
                    blockblob_service.put_block(container_name, file_to_upload, file_bytes, block_id)                    
                    
                    blocks.append(BlobBlock(id=block_id))
                    
                    file_bytes = file.read(block_size)
            
            blockblob_service.put_block_list(container_name, file_to_upload, blocks)
            
            print('3. Get the block list')
            blockslist = blockblob_service.get_block_list(container_name, file_to_upload, None, 'all')
            blocks = blockslist.committed_blocks

            print('4. Enumerate blocks in block blob')
            for block in blocks:
                print('Block ' + block.id)
        finally:
            print('5. Delete container')
            if blockblob_service.exists(container_name):
                blockblob_service.delete_container(container_name)

    # Manage properties of the Blob service, including logging and metrics settings, and the default service version.
    def set_service_properties(self, account):

        # Create an page blob service object
        blockblob_service = account.create_block_blob_service()

        print('1. Get Blob service properties')
        props = blockblob_service.get_blob_service_properties();

        retention = RetentionPolicy(enabled=True, days=5)
        logging = Logging(delete=True, read=False, write=True, retention_policy=retention)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=retention)
        minute_metrics = Metrics(enabled=False)

        try:
            print('2. Ovewrite Blob service properties')
            blockblob_service.set_blob_service_properties(logging=logging, hour_metrics=hour_metrics, minute_metrics=minute_metrics, target_version='2015-04-05')
        finally:
            print('3. Revert Blob service properties back to the original ones')
            blockblob_service.set_blob_service_properties(logging=props.logging, hour_metrics=props.hour_metrics, minute_metrics=props.minute_metrics, target_version='2015-04-05')

        print('4. Set Blob service properties completed')