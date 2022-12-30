import tweepy
import requests
import re
import math

# Replace these with your own Twitter API keys and secrets
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"
bearer_token = "YOUR_BEARER_TOKEKN"

# Replace this with your Google Translate API key
translate_api_key = "YOUR_GOOGLE_TRANSLATE_API_KEY"

# Authenticate with Twitter using the API keys and secrets
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Function generated with the following ChatGPT-Prompt:
# "Write a python function that converts a string into an array of strings. Each string in the array is shorter than
# 180 characters containing complete words from the original long string. Furthermore, the strings in the array are
# marked with an index from (1/n) to (n/n) where n is the length of the array."
def convert_to_array(long_string: str) -> [str]:
    # First, split the long string into a list of words
    words = long_string.split()

    # Next, calculate the number of strings we need to split the long string into.
    # We do this by dividing the total number of characters by 180, and rounding up
    # to the nearest integer using the math.ceil function.
    num_strings = math.ceil(len(long_string) / 180)

    # Initialize an empty list to hold the short strings
    short_strings = []

    # Initialize a counter to keep track of the current index
    index = 1

    # Initialize a temporary string to hold the current short string we are building
    temp_string = ""

    # Iterate over the list of words
    for word in words:
        # If adding the current word to the temp string would make it too long,
        # append the temp string to the list of short strings and reset the temp string.
        if len(temp_string) + len(word) > 180:
            short_strings.append(f"{temp_string} ({index}/{num_strings})")
            temp_string = ""
            index += 1

        # If the current word fits within the current temp string, add it to the temp string
        temp_string += word + " "

    # After the loop, add the remaining temp string to the list of short strings
    short_strings.append(f"{temp_string} ({index}/{num_strings})")

    # Return the list of short strings
    return short_strings

# Code for this function was created with #ChatGPT with this prompt:
# "write some code in python that detects an URL an removes it in a function"
def remove_urls(text: str) -> str:
    """Removes URLs from a given string.

    Args:
        text: A string that may contain URLs.

    Returns:
        A string with the URLs removed.
    """
    return re.sub(r"http\S+", "", text)


# Code generated with #ChatGPT with the prompt:
# "Can you create some python code that will monitor the twitter account "@erlangen_de" for new tweets, translate
# them from German to English and post the English translation followed by the url of the original tweet?"

# Set up a stream to monitor the twitter account "@erlangen_de"
class MyStream(tweepy.StreamingClient):
    def on_tweet(self, status):
        # If the tweet is in German, translate it to English
        # if status.lang == "de":

        print("Tweet :\n")
        text = remove_urls(status.data['text'])
        quote_tweet = status.data['id']
        print(text)
        # Use the Google Translate API to translate the tweet
        translate_url = "https://translation.googleapis.com/language/translate/v2"
        payload = {
            "q": text,
            "target": "en",
            "format": "text",
            "key": translate_api_key,
        }
        response = requests.post(translate_url, data=payload)
        translation = response.json()["data"]["translations"][0]["translatedText"]

        short_strings = convert_to_array(translation)
        url = "https://mobile.twitter.com/erlangen_de/status/" + quote_tweet
        tweet_id = -1
        # Post the English translation followed by the url of the original tweet
        for tweet in short_strings:
            tweet_text = tweet
            print(tweet)
            if tweet_id == -1:
                result = api.update_status(status=tweet_text, attachment_url=url)
                tweet_id = result.id
            else:
                tweet_text = "@erlangen_en " + tweet
                result = api.update_status(status=tweet_text, in_reply_to_status_id=tweet_id)
                tweet_id = result.id
            print(result)


my_stream = MyStream(bearer_token=bearer_token)
rules = my_stream.get_rules()
my_stream.delete_rules(rules.data)
my_stream.add_rules(tweepy.StreamRule('from:erlangen_de'))
my_stream.filter()  # The user ID for the twitter account "@erlangen_de"
