import praw
import pandas as pd

def has_bulleted_value(items):
    for item in items:
        # this newline starts with a bullet. assume it is part of a 'value' that is broken out by bullet points
        if item[0] == "*":
            return True
    return False      
            
def merge_bullets(items):

    already_merging = False
    index_to_merge_to = -1
    to_delete = [] #list of indices to delete
    for i, item in enumerate(items):
        if item[0] == "*":
            if already_merging:
                items[index_to_merge_to] = items[index_to_merge_to] + item
                to_delete.append(i)
            else:
                if i == 0:
                    # the first item in the list was a bullet point? ignore it
                    print("first item in the list had a bullet point. this shouldn't happen")
                else:
                    # we aren't already merging(aka second of > 1 bullet point scenario), and this isn't the first item in the list
                    # merge to the item before this, as this should be the first bullet, and the previous item should be this items key
                    index_to_merge_to = i - 1
                    already_merging = True
                    items[index_to_merge_to] = items[index_to_merge_to] + item
                    to_delete.append(i)
    items = [item for index, item in enumerate(items) if index not in to_delete]
    return items

def parse_comments(comments, text_to_match, data_frame):
    for topLevelComment in comments:
        if text_to_match in topLevelComment.body:
            for reply in topLevelComment.replies.list():
                item_list = []

                if "\n" in reply.body:
                     #if we have a newline char, treat the comment as newline delimited
                    item_list = reply.body.split("\n")
                else:
                    #fallback to delimit by unicode bullet point char if no newlines
                    item_list = reply.body.split(u'\u2022')

                # remove empty strings from split() operation
                item_list = list(filter(None, item_list))

                if has_bulleted_value(item_list):
                    #de-bullet value
                    item_list = merge_bullets(item_list)

                for item in item_list:

                    toAdd = []
                    if reply.author is None:
                        toAdd.append(reply.id)
                    else:
                        toAdd.append(reply.author.name)

                    key_value = item.split(':')

                    if len(key_value) == 2:
                        toAdd.append(key_value[0])
                        toAdd.append(key_value[1])
                        toAdd.append(reply.created_utc)
                        data_frame.loc[len(data_frame.index)] = toAdd
                    else:
                        #if this line can't be split into a key-value pair at this point, we don't care about it
                        print('Could not split this line into a key-val pair:', key_value)
    return data_frame

reddit = praw.Reddit(client_id="-TsA2La8qljlDcb7ZBsBrQ", client_secret="wSLMv_LSpy8gKjbcuL0Elmys9ho22g", user_agent="salary sharing thread webscraper", redirect_uri="http://localhost:8080")

junComments = reddit.submission(url="https://www.reddit.com/r/cscareerquestions/comments/vf0k9y/official_salary_sharing_thread_for_experienced/")
marComments = reddit.submission(url="https://www.reddit.com/r/cscareerquestions/comments/tgvh4i/official_salary_sharing_thread_for_experienced/")
decComments = reddit.submission(url="https://www.reddit.com/r/cscareerquestions/comments/rj2q04/official_salary_sharing_thread_for_experienced/")

junComments.comments.replace_more()
marComments.comments.replace_more()
decComments.comments.replace_more()

text_to_match = 'Region - **US Medium CoL**'

data_frame = pd.DataFrame(columns=['author', 'key', 'value', 'utc_time'])

data_frame = parse_comments(junComments.comments, text_to_match, data_frame)
data_frame = pd.concat([data_frame, parse_comments(marComments.comments, text_to_match, pd.DataFrame(columns=['author', 'key', 'value', 'utc_time']))])
data_frame = pd.concat([data_frame, parse_comments(decComments.comments, text_to_match, pd.DataFrame(columns=['author', 'key', 'value', 'utc_time']))])

data_frame = data_frame.set_index('author')
data_frame.to_csv('juneData.csv')

