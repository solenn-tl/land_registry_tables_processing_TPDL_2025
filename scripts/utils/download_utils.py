import requests
import os
from dan.datasets.download.images import ImageDownloader

def download_image(save_path, url, element_uuid):
    """
    Download an image from the given URL and save it to the specified path.

    :param url: The URL of the image to download.
    :param save_path: The local path where the image will be saved.
    :param element_uuid UUID of the corresponding element in Arkindex
    """
    try:
        # Send a HTTP GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Open a local file with write-binary mode
        with open(save_path + "/" + element_uuid + '.jpg', 'wb') as file:
            # Iterate over the response data in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Image successfully downloaded and saved to {save_path}/{element_uuid}.jpg")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {element_uuid} : {e}")

def download_images_from_list(save_path, urls, elements_uuid, subfolders=None):
    """
    Download multiple images from a list of URLs and save them to the specified directory.
    
    :param save_path: The local path where the images will be saved.
    :param urls: A list of URLs of the images to download.
    :param element_uuid: A list of UUID of the elements associated with the images in Arkindex
    :param subfolders: A list of folder's name where the images have to be saved
    """
    #If images folder not exists, create it
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #If subset folder not exists, create it
    if subfolders != None:
        for s in list(set(subfolders)):
            if not os.path.exists(save_path + '/' + s):
                os.makedirs(save_path + '/' + s)
        for i, (url, element_uuid, subpath) in enumerate(zip(urls,elements_uuid,subfolders)):
            # Download the image
            download_image(save_path + '/' + subpath, url, element_uuid)
    else:
        for i, (url, element_uuid) in enumerate(zip(urls,elements_uuid)):
            # Download the image
            download_image(save_path, url, element_uuid)

def download_iiif_images_using_arkindex(df, base_url, column_arkindex_uuid, column_elem_coordinates, column_image_name, save_directory, column_subfolder=None):
    """
    Download multiple images described in ARkindex and stored in IIIF server
    
    :param df: Dataframe containing informations of the images
    :param base_url: URL of the IIIF server
    :param column_arkindex_uuid: Name of the column of the df containing the UUID of the elements
    :param column_elem_coordinates: Name of the column of the df containing the coordinates of the elements on the image
    :param column_image_name: Name of the column containg the specific path of the image on the IIIF server
    :param save_directory: Local directory where the images have to be saved
    :param column_subfolder: Name of the column of the df containing the name of the subfolder where the images have to be saved
    """ 
    # Create an instance of ImageDownloader
    downloader = ImageDownloader()
    #Init empty lists
    urls, elements_uuid = [], []
    if column_subfolder != None:
        subfolders_ = []

    for _, row in df.iterrows():  
        # Elements UUID
        elements_uuid.append(row[column_arkindex_uuid])
        # Rebuild elements IIIF URL
        coords = row[column_elem_coordinates]
        image_name = row[column_image_name]
        full_url = downloader.build_iiif_url(coords, base_url + image_name)
        urls.append(full_url)
        #Subfolder's names
        if column_subfolder != None:
            subfolders_.append(row[column_subfolder])

    #Download images
    if column_subfolder != None:
        download_images_from_list(save_directory, urls, elements_uuid, subfolders_)
    else:
        download_images_from_list(save_directory, urls, elements_uuid)