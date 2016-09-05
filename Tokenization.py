import html.parser
import re


class TweetTokenizer:
    def __call__(self, t):
        """
        Tokenizes a string, but keeps urls intact.
        :param t: String
        :return: List
        """
        t = str(t)
        t = html.parser.HTMLParser().unescape(t)
        links_re = re.compile('http[s]?://\S+')
        split_re = re.compile('[\s\r\n\.,\?!]+')
        links = links_re.findall(t)  # exctract links
        for l in links:
            t = t.replace(l, '')
        retVal = split_re.split(t) + links  # add unmodified links
        return [str(x).strip() for x in retVal]  # remove leading and trailing whitespace
