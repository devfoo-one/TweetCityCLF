import re


class TextProcessor:
    config = {
        'remove_urls': False,
        'remove_user_mentions': False,
        'transform_lowercase': True,
        'remove_hashtags': False,
        'blind_urls': False,
        'expand_urls': True
    }

    def __init__(self, blind_urls=False, remove_urls=False, remove_user_mentions=False, remove_hashtags=False,
                 transform_lowercase=True, expand_urls=True):
        self.config['remove_urls'] = remove_urls
        self.config['remove_user_mentions'] = remove_user_mentions
        self.config['transform_lowercase'] = transform_lowercase
        self.config['remove_hashtags'] = remove_hashtags
        self.config['blind_urls'] = blind_urls
        self.config['expand_urls'] = expand_urls

    def digest(self, tweet):
        """Processes a tweet object (as given from the streaming api) and returns a string."""
        tweet_text = tweet['text']

        """remove URLs"""
        if self.config['remove_urls']:
            # collect all url strings (ugly but works)
            urls = []
            for url in tweet['entities']['urls']:
                urls.append(url['url'])
            try:
                for url in tweet['entities']['media']:
                    urls.append(url['url'])
            except KeyError:
                pass
            for url in urls:
                tweet_text = tweet_text.replace(url, '')

        """blind URLs"""
        if self.config['blind_urls']:
            for url in tweet['entities']['urls']:
                tweet_text = tweet_text.replace(url['url'], '[URL]')
            try:
                for url in tweet['entities']['media']:
                    tweet_text = tweet_text.replace(url['url'], '[MEDIA_URL]')
            except KeyError:
                pass

        """remove user mentions"""
        if self.config['remove_user_mentions']:
            for mention in tweet['entities']['user_mentions']:
                tweet_text = tweet_text.replace('@' + mention['screen_name'], '')

        """remove hashtags"""
        if self.config['remove_hashtags']:
            for hashtag in tweet['entities']['hashtags']:
                tweet_text = tweet_text.replace('#' + hashtag['text'], '')

        """transform to lowercase"""
        if self.config['transform_lowercase']:
            tweet_text = tweet_text.lower()

        """expand urls"""
        if self.config['expand_urls']:
            urls = []
            for url in tweet['entities']['urls']:
                urls.append((url['url'], url['expanded_url']))
            try:
                for url in tweet['entities']['media']:
                    urls.append((url['url'], url['expanded_url']))
            except KeyError:
                pass
            for url, expanded_url in urls:
                tweet_text = tweet_text.replace(url, expanded_url)

        return tweet_text

    def __call__(self, tweet):
        return self.digest(tweet)

    def __str__(self):
        return ', '.join([attr + '=' + str(val) for attr, val in self.config.items()])