import instaloader
import concurrent.futures
from django.http import HttpResponse
import os
from django.shortcuts import render, redirect
from django.db import models
# from .models import download_user_data
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import download_instagram_media
from .models import download_instagram_profile_photo
from .models import DownloadStatistics
from django.shortcuts import render
from django.db.models import F
# from django.core.files import File


def process_post(post):
    return post.likes, post.comments, post.caption_hashtags

def retrieve_likes_comments_and_tags(posts):
    # Use concurrent processing to calculate likes, comments, and tags in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_post, posts))

    # Calculate the total likes, comments, and tags
    total_likes = sum(likes for likes, _, _ in results)
    total_comments = sum(comments for _, comments, _ in results)

    # Count the total hashtags used
    all_tags = [tag for _, _, tags in results for tag in tags]
    total_tags = len(all_tags)

    return total_likes, total_comments, total_tags

def get_instagram_info(request):
    if request.method == 'POST':
        username = request.POST['username']
        L = instaloader.Instaloader()

        user_info = {}  # Initialize a dictionary to store user information

        try:
            profile = instaloader.Profile.from_username(L.context, username)

            # Retrieve the user's posts
            posts = list(profile.get_posts())

            # Retrieve likes, comments, and tags in parallel
            total_likes, total_comments, total_tags = retrieve_likes_comments_and_tags(posts)

            # Get the desired information
            user_info['username'] = username
            user_info['following_count'] = profile.followees
            user_info['followers_count'] = profile.followers
            user_info['total_posts'] = profile.mediacount
            user_info['igtv_posts'] = profile.igtvcount
            user_info['is_private'] = profile.is_private
            user_info['bio'] = profile.biography
            user_info['profile_picture'] = profile.profile_pic_url
            user_info['external_url'] = profile.external_url
            user_info['total_likes'] = total_likes
            user_info['total_comments'] = total_comments
            user_info['total_hashtags'] = total_tags

            # Add the profile picture URL to the user_info dictionary
            user_info['profile_picture_url'] = profile.profile_pic_url

        except instaloader.exceptions.ProfileNotExistsException:
            user_info['error'] = f"Profile '{username}' does not exist."
        except Exception as e:
            user_info['error'] = f"An error occurred for '{username}': {str(e)}"

        return render(request, 'get_instagram_info.html', {'user_info': user_info})
    else:
        return render(request, 'get_instagram_info.html')

    
from django.shortcuts import render, redirect

def download_yes_view(request):
    if request.method == 'POST':
        # Handle the "Yes" action here
        # Redirect to your download.html page
        return redirect('download_yes')  # Replace 'download_page' with your actual URL name for the download page

def download_no_view(request):
    if request.method == 'POST':
        # Handle the "No" action here
        # Redirect to some other page or perform any other action
        return redirect('download_no')  # Replace 'some_other_page' with your desired URL name



# ---------------------------------

def download_user_data(username, download_images=True, download_videos=True, download_txt=True, num_posts=10):
    # Create an instance of the Instaloader class
    L = instaloader.Instaloader()

    try:
        # Retrieve the profile details
        profile = instaloader.Profile.from_username(L.context, username)

        # Display the total number of posts
        total_posts = profile.mediacount
        print(f"Total posts by {username}: {total_posts}")

        # Calculate the number of posts to download
        if num_posts.lower() == 'all':
            num_posts = total_posts
        else:
            num_posts = int(num_posts)

        # Define the target folder
        target_folder = f"{username}_posts"

        # Ensure the target folder exists
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Define a list of file extensions to delete based on user preferences
        extensions_to_delete = []

        if not download_images:
            extensions_to_delete.extend(['.jpg', '.png', '.jpeg'])
        if not download_videos:
            extensions_to_delete.extend(['.mp4'])
        if not download_txt:
            extensions_to_delete.extend(['.txt'])

        # Iterate through the user's posts and download selected content
        for post in profile.get_posts():
            if num_posts <= 0:
                break

            # Check if the user wants to download images
            if download_images and post.typename == 'GraphImage':
                L.download_post(post, target=target_folder)
                print(f"Downloaded image: {post.url}")
                num_posts -= 1

            # Check if the user wants to download videos
            if download_videos and post.typename == 'GraphVideo':
                L.download_post(post, target=target_folder)
                print(f"Downloaded video: {post.url}")
                num_posts -= 1

            # Check if the user wants to download captions
            if download_txt:
                # Download caption in a text file
                caption_text = f"{post.caption}\n"
                with open(f"{target_folder}/{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}.txt", 'w') as file:
                    file.write(caption_text)
                print(f"Downloaded TXT caption: {post.url}")
                num_posts -= 1

        # Delete files based on user preferences
        for file_extension in extensions_to_delete:
            # Get a list of all files in the current directory
            all_files = os.listdir(target_folder)

            # Iterate over all files and delete those that match the extension
            for file in all_files:
                if file.lower().endswith(file_extension):
                    os.remove(os.path.join(target_folder, file))
                    print(f"Deleted {file_extension} file: {file}")

        # Delete '.json.xz' files regardless of selection
        all_files = os.listdir(target_folder)
        for file in all_files:
            if file.lower().endswith('.json.xz'):
                os.remove(os.path.join(target_folder, file))
                print(f"Deleted .json.xz file: {file}")

        # Update the download count in the DownloadStatistics model
        download_statistic, created = DownloadStatistics.objects.get_or_create(username=username)
        download_statistic.download_count += 1
        download_statistic.save()


        print("Download completed!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def download_data_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        download_images = request.POST.get('download_images') == 'on'
        download_videos = request.POST.get('download_videos') == 'on'
        download_txt = request.POST.get('download_txt') == 'on'
        num_posts = request.POST.get('num_posts')  # No default value

        # If num_posts is not provided or is an empty string, set it to 'all'
        if not num_posts:
            num_posts = 'all'

        # Call your download_user_data function here with the selected options
        download_user_data(username, download_images, download_videos, download_txt, num_posts)

        # Redirect or render a page to indicate download started
        return HttpResponse("Download started. Check it has been downloaded or not")  # Customize this response as needed

    return render(request, 'download_data.html')


def download_media_view(request):
    if request.method == 'POST':
        link = request.POST.get('media_link')

        # Call your download_instagram_media function to download the media
        download_instagram_media(link)

        # Customize the response message as needed
        return HttpResponse("Media download started. Check it has been downloaded or not")

    return render(request, 'download_media.html')


def download_profile_photo_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        # Call your download_instagram_profile_photo function to download the profile photo
        download_instagram_profile_photo(username)

        # Customize the response message as needed
        return render(request, 'download_message.html', {'message': 'Profile photo download started. Check it has been downloaded or not'})

    return render(request, 'download_profile_photo.html')


import matplotlib.pyplot as plt
import io
import base64

def get_pie_chart_image(usernames, download_counts):
    """Generates a pie chart image from the given usernames and download counts.

    Args:
        usernames: A list of usernames.
        download_counts: A list of download counts.

    Returns:
        A base64-encoded PNG image as a string.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(download_counts, labels=usernames, autopct='%1.1f%%', startangle=140)
    ax.set_title('Download Statistics')
    ax.axis('equal')

    # Create a buffer to store the plot image.
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image as a base64 string
    base64_image = base64.b64encode(buffer.read()).decode()

    return base64_image

def download_statistics_view(request):
    # Fetch data from the database
    download_stats = DownloadStatistics.objects.all()

    usernames = [stat.username for stat in download_stats]
    download_counts = [stat.download_count for stat in download_stats]

    # Generate the pie chart image as a base64 string
    pie_chart_image = get_pie_chart_image(usernames, download_counts)

    # Pass the base64 image to the template
    context = {
        'pie_chart_image': pie_chart_image
    }

    return render(request, 'download_statistics.html', context)

def dashboard_view(request):
  return render(request, 'dashboards.html')


