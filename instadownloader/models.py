from django.db import models
import instaloader
import os
from django.contrib.auth.models import User

# def download_user_data(username, download_images=True, download_videos=True, download_txt=True, num_posts=10):
#     # Create an instance of the Instaloader class
#     L = instaloader.Instaloader()

#     try:
#         # Retrieve the profile details
#         profile = instaloader.Profile.from_username(L.context, username)

#         # Display the total number of posts
#         total_posts = profile.mediacount
#         print(f"Total posts by {username}: {total_posts}")

#         # Calculate the number of posts to download
#         if num_posts.lower() == 'all':
#             num_posts = total_posts
#         else:
#             num_posts = int(num_posts)

#         # Define the target folder
#         target_folder = f"{username}_posts"

#         # Ensure the target folder exists
#         if not os.path.exists(target_folder):
#             os.makedirs(target_folder)

#         # Define a list of file extensions to delete based on user preferences
#         extensions_to_delete = []

#         if not download_images:
#             extensions_to_delete.extend(['.jpg', '.png', '.jpeg'])
#         if not download_videos:
#             extensions_to_delete.extend(['.mp4'])
#         if not download_txt:
#             extensions_to_delete.extend(['.txt'])

#         # Iterate through the user's posts and download selected content
#         for post in profile.get_posts():
#             if num_posts <= 0:
#                 break

#             # Check if the user wants to download images
#             if download_images and post.typename == 'GraphImage':
#                 L.download_post(post, target=target_folder)
#                 print(f"Downloaded image: {post.url}")
#                 num_posts -= 1

#             # Check if the user wants to download videos
#             if download_videos and post.typename == 'GraphVideo':
#                 L.download_post(post, target=target_folder)
#                 print(f"Downloaded video: {post.url}")
#                 num_posts -= 1

#             # Check if the user wants to download captions
#             if download_txt:
#                 # Download caption in a text file
#                 caption_text = f"{post.caption}\n"
#                 with open(f"{target_folder}/{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}.txt", 'w') as file:
#                     file.write(caption_text)
#                 print(f"Downloaded TXT caption: {post.url}")
#                 num_posts -= 1

#         # Delete files based on user preferences
#         for file_extension in extensions_to_delete:
#             # Get a list of all files in the current directory
#             all_files = os.listdir(target_folder)

#             # Iterate over all files and delete those that match the extension
#             for file in all_files:
#                 if file.lower().endswith(file_extension):
#                     os.remove(os.path.join(target_folder, file))
#                     print(f"Deleted {file_extension} file: {file}")

#         # Delete '.json.xz' files regardless of selection
#         all_files = os.listdir(target_folder)
#         for file in all_files:
#             if file.lower().endswith('.json.xz'):
#                 os.remove(os.path.join(target_folder, file))
#                 print(f"Deleted .json.xz file: {file}")

#         print("Download completed!")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

def download_instagram_media(link):
    # Create an Instaloader instance.
    L = instaloader.Instaloader()

    try:
        # Load the media from the URL.
        media = instaloader.Post.from_shortcode(L.context, link.split("/")[-2])

        # Get the username of the owner of the media
        username = media.owner_username

        # Specify the target folder where the media will be saved.
        target_folder = f"{username}_media"

        # Ensure the target folder exists
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Download the media.
        L.download_post(media, target=target_folder)

        print(f"Downloaded media from {link} to {target_folder}")
    except instaloader.exceptions.InstaloaderException as e:
        print(f"An error occurred while downloading '{link}': {str(e)}")

def download_instagram_profile_photo(username):
    """Downloads the profile photo of an Instagram user.

    Args:
        username (str): The username of the Instagram user.

    Returns:
        None
    """

    # Create an Instaloader instance.
    L = instaloader.Instaloader()

    try:
        # Check if the profile is private
        profile = instaloader.Profile.from_username(L.context, username)

        if profile.is_private:
            # The profile is private, ask for username and password
            insta_username = input("Enter your Instagram username: ")
            insta_password = input("Enter your Instagram password: ")

            try:
                L.context.login(insta_username, insta_password)
            except instaloader.exceptions.BadCredentialsException:
                print("Incorrect username or password or 2FA is enabled. Please check your credentials.")
                return

        # Get the profile of the Instagram user.
        profile = instaloader.Profile.from_username(L.context, username)

        # Download the profile photo of the user.
        L.download_profilepic(profile)

        print('The profile photo of the user has been downloaded successfully!')

    except instaloader.exceptions.InstaloaderException as e:
        print(f"An error occurred: {str(e)}")


class DownloadStatistics(models.Model):
    username = models.CharField(max_length=255, unique=True)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username
    


