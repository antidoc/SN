import json
import requests
import random

with open("settings.json", "r") as config_file:
    config = json.load(config_file)

base_url = config["base_url"]
number_of_users = config["number_of_users"]
max_posts_per_user = config["max_posts_per_user"]
max_likes_per_user = config["max_likes_per_user"]
user_tokens = {}


def register_user(user_number):
    login_url = f"{base_url}/api/users/"
    user = f"user{user_number}"
    json_data = {
        "new_user":{
            "email": f"{user}@local.org",
            "username": user,
            "password": "Test123!"
        }
    }
    r = requests.post(login_url, json=json_data)
    user_tokens[user] = r.json()["access_token"]["access_token"]
    return f"User {user} was registered successfully "


def create_post(user, token):
    post_creation_url = f"{base_url}/api/posts/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    json_data = {
        "new_post": {
            "title": f"{user} post",
            "content": "Lorem Ipsum bla-bla-bla"
        }
    }
    r = requests.post(post_creation_url, headers=headers, json=json_data)
    return f"{user}'s post was created successfully"

def get_posts_ids():
    post_ids = []
    post_number_url = f"{base_url}/api/posts/"
    r = requests.get(post_number_url)
    for post in r.json():
        post_ids.append(post["id"])
    return post_ids

def set_like_on_post(post_number, token):
    set_like_on_post_url = f"{base_url}/api/activity/{post_number}/like"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    r = requests.post(set_like_on_post_url, headers=headers)
    return f"Post {post_number} was liked successfully"

if __name__ == "__main__":
    for i in range(number_of_users+1):
        print(register_user(i))

    for key, value in user_tokens.items():
        posts_to_create = random.randint(0, max_posts_per_user)
        for i in range(posts_to_create):
            print(create_post(key, value))

    post_ids = get_posts_ids()
    for key, value in user_tokens.items():
        posts_to_like = random.randint(0, max_likes_per_user)
        for i in range(posts_to_like):
            set_like_on_post(random.choice(post_ids), value)



