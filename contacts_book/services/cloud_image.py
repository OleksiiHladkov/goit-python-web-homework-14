import hashlib
import cloudinary
import cloudinary.uploader

from contacts_book.conf.config import settings


class CloudImage():
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_avatar(email: str):
        """
        The generate_name_avatar function takes an email address as a string and returns the name of the avatar image file.
        The function uses SHA256 to hash the email address, then truncates it to 12 characters.
        It then appends that string to &quot;contacts_book_avatars/&quot; and returns it.
        
        :param email: str: Specify the type of parameter that is expected to be passed into the function
        :return: A string with a name of the avatar
        """
        name = hashlib.sha256(email.encode("utf-8")).hexdigest()[:12]
        return f"contacts_book_avatars/{name}"
    
    @staticmethod
    def upload(file, public_id: str):
        """
        The upload function takes a file and public_id as arguments.
            The function then uploads the file to Cloudinary with the given public_id, overwriting any existing files with that id.
            It returns a dictionary containing information about the uploaded image.
        
        :param file: Upload the file to cloudinary
        :param public_id: str: Specify the name of the file that will be uploaded to cloudinary
        :return: A dictionary
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r
    
    @staticmethod
    def get_url_for_avatar(public_id: str, r):
        """
        The get_url_for_avatar function takes a public_id and an optional resource dictionary as arguments.
        The function returns the URL for the avatar image with a width of 250 pixels, height of 250 pixels, 
        and fill crop mode. The version is set to the value in r['verison'] if it exists.
        
        :param public_id: str: Identify the image to be uploaded
        :param r: Get the version of the image
        :return: A url for the avatar
        """
        src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=r.get('version'))
        return src_url