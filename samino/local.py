import os
import json
import base64
import requests
from uuid import UUID
from time import timezone
from typing import BinaryIO
from binascii import hexlify
from time import time as timestamp
from json_minify import json_minify

from .lib import api
from .lib import headers
from .lib.objects import *
from .lib import CheckExceptions


class Local:
    def __init__(self, comId: str, proxies: dict = None):
        self.proxies = proxies
        self.comId = comId
        self.uid = headers.uid
        self.headers = headers.Headers().headers
        self.web_headers = headers.Headers().web_headers

    def get_video_rep_info(self, chatId: str):
        req = requests.get(api(f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return RepInfo(req.json())

    def claim_video_rep(self, chatId: str):
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return RepInfo(req.json())

    def join_chat(self, chatId: str = None):
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.uid}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def upload_media(self, file: BinaryIO, fileType: str):
        if fileType == "audio": type = "audio/aac"
        elif fileType == "image": type = "image/jpg"
        else: raise TypeError("")

        data = file.read()
        header = self.headers
        header["content-type"] = type
        header["content-length"] = str(len(data))

        req = requests.post(api("/g/s/media/upload"), data=data, headers=header)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return req.json()["mediaValue"]

    def leave_chat(self, chatId: str = None):
        req = requests.delete(api(f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.uid}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def get_member_following(self, userId: str = None, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_member_followers(self, userId: str = None, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}"))
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_chat_threads(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return ThreadList(req.json()["threadList"]).ThreadList

    def get_member_visitors(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return VisitorsList(req.json()["visitors"]).VisitorsList

    def get_chat_messages(self, chatId: str, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return MessageList(req.json()["messageList"]).MessageList

    def get_user_info(self, userId: str):
        req = requests.get(api(f"/x{self.comId}/s/user-profile/{userId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfile(req.json()["userProfile"]).UserProfile

    def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):
        sorting = sorting.lower()

        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"
        else: raise TypeError("حط تايب يا حمار")  # Not me typed this its (a7rf)

        req = requests.get(api(f"/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommentList(req.json()["commentList"]).CommentList

    def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        if type == "recent": type = "recent"
        elif type == "banned": type = "banned"
        elif type == "featured": type = "featured"
        elif type == "leaders": type = "leaders"
        elif type == "curators": type = "curators"

        req = requests.get(api(f"/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_chat_members(self, start: int = 0, size: int = 25, chatId: str = None):
        req = requests.get(api(f"/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["memberList"]).UserProfileList

    def get_chat_info(self, chatId: str):
        req = requests.get(api(f"/x{self.comId}/s/chat/thread/{chatId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Thread(req.json()["thread"]).Thread

    def get_online_users(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_public_chats(self, type: str = "recommended", start: int = 0, size: int = 50):
        req = requests.get(api(f"/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return ThreadList(req.json()["threadList"]).ThreadList

    def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, snippetLink: str = None, ytVideo: str = None, snippetImage: BinaryIO = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):
        if message is not None and file is None: message = message.replace("[@", "‎‏").replace("@]", "‬‭")

        mentions = []
        if mentionUserIds:
            for mention_uid in mentionUserIds: mentions.append({"uid": mention_uid})

        if embedImage: embedImage = [[100, self.upload_media(embedImage, "image"), None]]

        data = {
            "type": messageType,
            "content": message,
            "attachedObject": {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent,
                "mediaList": embedImage
            },
            "extensions": {"mentionedArray": mentions},
            "clientRefId": int(timestamp() / 10 % 100000000),
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["replyMessageId"] = replyTo

        if stickerId:
            data["content"] = None
            data["stickerId"] = stickerId
            data["type"] = 3

        if snippetLink and snippetImage:
            data["attachedObject"] = None
            data["extensions"]["linkSnippetList"] = [{
                "link": snippetLink,
                "mediaType": 100,
                "mediaUploadValue": base64.b64encode(snippetImage.read()).decode(),
                "mediaUploadValueContentType": "image/png"
            }]

        if ytVideo:
            data["content"] = None
            data["mediaType"] = 103
            data["mediaValue"] = ytVideo

        if file:
            data["content"] = None

            if fileType == "audio":
                data["type"] = 2
                data["mediaType"] = 110

            elif fileType == "image":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/jpg"
                data["mediaUhqEnabled"] = False

            elif fileType == "gif":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/gif"
                data["mediaUhqEnabled"] = False

            else: raise TypeError("")

            data["mediaUploadValue"] = base64.b64encode(file.read()).decode()
            data["attachedObject"] = None
            data["extensions"] = None

        data = json.dumps(data)
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/message"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def send_web_message(self, chatId: str, message: str = None, messageType: int = 0, icon: str = None, comId: str = None):
        if comId: self.comId = comId

        data = {
            "ndcId": f"x{self.comId}",
            "threadId": chatId,
            "message": {"content": message, "mediaType": 0, "type": messageType, "sendFailed": False, "clientRefId": 0}
        }

        if icon:
            data["message"]["content"] = None
            data["message"]["uploadId"] = 0
            data["message"]["mediaType"] = 100
            data["message"]["mediaValue"] = icon

        req = requests.post("https://aminoapps.com/api/add-chat-message", json=data, headers=self.web_headers)
        try:
            if req.json()["code"] != 200: return CheckExceptions(req.json())
            else: Json(req.json())
        except: return CheckExceptions(req.json())
        return Json(req.json())

    def unfollow(self, userId: str):
        req = requests.post(api(f"/x{self.comId}/s/user-profile/{userId}/member/{self.uid}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def follow(self, userId: [str, list]):
        data = {"timestamp": int(timestamp() * 1000)}

        if isinstance(userId, str): url = api(f"/x{self.comId}/s/user-profile/{userId}/member")
        elif isinstance(userId, list):
            url = api(f"/x{self.comId}/s/user-profile/{self.uid}/joined")
            data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
        else: raise TypeError("Please put str or list of userId")

        req = requests.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def start_chat(self, userId: [str, list], title: str = None, message: str = None, content: str = None, type: int = 0):
        if isinstance(userId, list): userIds = userId
        elif isinstance(userId, str): userIds = [userId]
        else: raise TypeError("Please put a str or list of userId")

        data = json.dumps({
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "type": type,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/chat/thread"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_to_chat(self, userId: [str, list], chatId: str = None):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise TypeError("")

        data = json.dumps({"uids": userIds, "timestamp": int(timestamp() * 1000)})

        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/member/invite"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None):
        data = {
            "address": None,
            "latitude": 0,
            "longitude": 0,
            "mediaList": None,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        }

        if nickname: data["nickname"] = nickname
        if icon: data["icon"] = self.upload_media(icon, "image")
        if content: data["content"] = content
        if backgroundColor: data["extensions"]["style"] = {"backgroundColor": backgroundColor}
        if backgroundImage: data["extensions"]["style"] = {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}
        if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

        data = json.dumps(data)
        req = requests.post(api(f"/x{self.comId}/s/user-profile/{self.uid}"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def edit_chat(self, chatId: str, title: str = None, content: str = None, icon: str = None, background: str = None, keywords: list = None, announcement: str = None, pinAnnouncement: bool = None):
        res, data = [], {"timestamp": int(timestamp() * 1000)}

        if title: data["title"] = title
        if content: data["content"] = content
        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if announcement: data["extensions"]["announcement"] = announcement
        if pinAnnouncement: data["extensions"]["pinAnnouncement"] = pinAnnouncement
        if background:
            data = json.dumps({"media": [100, background, None], "timestamp": int(timestamp() * 1000)})
            req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.uid}/background"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        data = json.dumps(data)
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        res.append(Json(req.json()))
        return res

    def chat_settings(self, chatId: str, viewOnly: bool = False, doNotDisturb: bool = True, canInvite: bool = False, canTip: bool = None, pin: bool = None, coHosts: [str, list] = None):
        res = []

        if doNotDisturb:
            if doNotDisturb: opt = 2
            else: opt = 1

            data = json.dumps({"alertOption": opt, "timestamp": int(timestamp() * 1000)})
            req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.uid}/alert"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if viewOnly:
            if viewOnly: viewOnly = "enable"
            else: viewOnly = "disable"

            req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/view-only/{viewOnly}"), headers=self.headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canInvite:
            if canInvite: canInvite = "enable"
            else: canInvite = "disable"

            req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/{canInvite}"), headers=self.headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canTip:
            if canTip: canTip = "enable"
            else: canTip = "disable"

            req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/{canTip}"), headers=self.headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if pin:
            if pin: pin = "pin"
            else: pin = "unpin"

            req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/{pin}"), headers=self.headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if coHosts:
            data = json.dumps({"uidList": coHosts, "timestamp": int(timestamp() * 1000)})
            req = requests.post(api(f"{self.comId}/s/chat/thread/{chatId}/co-host"), data=data, headers=headers.Headers(data=data).headers)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        return res

    def vote_comment(self, blogId: str, commentId: str, value: bool = True):
        if value: value = 1
        else: value = -1

        data = json.dumps({"value": value, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def like_blog(self, blogId: str = None, wikiId: str = None):
        data = json.dumps({"value": 4, "timestamp": int(timestamp() * 1000)})

        if blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/vote?cv=1.2&value=4")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/vote?cv=1.2&value=4")
        else: raise TypeError("Please put wiki or blog Id")

        req = requests.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unlike_blog(self, blogId: str = None, wikiId: str = None):
        if blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/vote?eventSource=FeedList")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/vote?eventSource=FeedList")
        else: raise TypeError("Please put wikiId or blogId")

        req = requests.delete(url, headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def change_titles(self, userId: str, titles: list, colors: list):
        t = []
        for title, color in zip(titles, colors): t.append({"title": title, "color": color})
        data = json.dumps({"adminOpName": 207, "adminOpValue": {"titles": t}, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/user-profile/{userId}/admin"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def like_comment(self, commentId: str, blogId: str = None, wikiId: str = None, userId: str = None):
        data = json.dumps({"value": 1})
        if blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/vote?cv=1.2&value=1")
        elif userId: url = api(f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1")
        else: raise TypeError("Please put a wiki or user or blog Id")

        req = requests.post(url, data=data, headers=headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unlike_comment(self, commentId: str, blogId: str = None, wikiId: str = None, userId: str = None):
        if blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView")
        elif userId: url = api(f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView")
        else: raise TypeError("Please put a wiki or user or blog Id")

        req = requests.delete(url, headers=headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def comment(self, comment: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False):
        data = {"content": comment, "timestamp": int(timestamp() * 1000)}

        if replyTo: data["respondTo"] = replyTo
        if isGuest: comType = "g-comment"
        else: comType = "comment"
        if userId: url = api(f"/x{self.comId}/s/user-profile/{userId}/{comType}")
        elif blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/{comType}")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/{comType}")
        else: raise TypeError("Please put a wiki or user or blog Id")

        data = json.dumps(data)
        req = requests.post(url, data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId: url = api(f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}")
        elif blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}")
        else: raise TypeError(" ")

        req = requests.delete(url, headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def vote_poll(self, blogId: str, optionId: str):
        data = json.dumps({"value": 1, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_blog_info(self, blogId: str = None, wikiId: str = None):
        if blogId: url = api(f"/x{self.comId}/s/blog/{blogId}")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}")
        else: raise TypeError("Please put a wiki or blog Id")

        req = requests.get(url, headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Blog(req.json()["blog"]).Blog

    def get_blogs(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/feed/featured?start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return BlogList(req.json()["featuredList"]).BlogList

    def get_blogs_more(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/feed/featured-more?start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return BlogList(req.json()["blogList"]).BlogList

    def get_blogs_all(self, start: int = 0, size: int = 25, pagingType: str = "t"):
        req = requests.get(api(f"/x{self.comId}/s/feed/blog-all?pagingType={pagingType}&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return RecentBlogs(req.json()["blogList"]).RecentBlogs

    def tip_coins(self, coins: int, chatId: str = None, blogId: str = None, wikiId: str = None, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(os.urandom(16)).decode("ascii")))
        data = {"coins": int(coins), "tippingContext": {"transactionId": transactionId}, "timestamp": int(timestamp() * 1000)}

        if chatId: url = api(f"/x{self.comId}/s/chat/thread/{chatId}/tipping")
        elif blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/tipping")
        elif wikiId:
            url = api(f"/x{self.comId}/s/tipping")
            data["objectType"] = 2
            data["objectId"] = wikiId
        else: raise TypeError("Please put a wiki or chat or blog Id")

        data = json.dumps(data)
        req = requests.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def check_in(self, timezone: int = 180):
        data = json.dumps({"timezone": timezone, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/check-in"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def check_in_lottery(self, timezone: int = 180):
        data = json.dumps({"timezone": timezone, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/check-in/lottery"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):
        data = {"adminOpName": 102, "timestamp": int(timestamp() * 1000)}
        if asStaff and reason: data["adminOpNote"] = {"content": reason}
        data = json.dumps(data)
        if asStaff: req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        else: req = requests.delete(api(f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def invite_by_host(self, chatId: str, userId: [str, list]):
        data = json.dumps({"uidList": userId, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/avchat-members"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def strike(self, userId: str, time: int, title: str = None, reason: str = None):
        data = json.dumps({
            "uid": userId,
            "title": title,
            "content": reason,
            "attachedObject": {"objectId": userId, "objectType": 0},
            "penaltyType": 1,
            "penaltyValue": time,
            "adminOpNote": {},
            "noticeType": 4,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/notice"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def ban(self, userId: str, reason: str, banType: int = None):
        data = json.dumps({
            "reasonType": banType,
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/user-profile/{userId}/ban"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unban(self, userId: str, reason: str = "هذا العضو كان شاطر اخر كم يوم"):
        data = json.dumps({
            "note": {"content": reason},
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/user-profile/{userId}/unban"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def hide(self, note: str = None, blogId: str = None, userId: str = None, wikiId: str = None, chatId: str = None):
        opN, opV = 110, 9
        if userId:
            opN = 18
            opV = None
            url = api(f"/x{self.comId}/s/user-profile/{userId}/admin")
        elif blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/admin")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/admin")
        elif chatId: url = api(f"/x{self.comId}/s/chat/thread/{chatId}/admin")
        else: raise TypeError("Please put a wiki or user or chat or blog Id")

        data = {"adminOpNote": {"content": note}, "adminOpName": opN, "adminOpValue": opV, "timestamp": int(timestamp() * 1000)}
        req = requests.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unhide(self, note: str = None, blogId: str = None, userId: str = None, wikiId: str = None, chatId: str = None):
        opN, opV = 110, 0

        if userId:
            opN = 19
            url = api(f"/x{self.comId}/s/user-profile/{userId}/admin")
        elif blogId: url = api(f"/x{self.comId}/s/blog/{blogId}/admin")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}/admin")
        elif chatId: url = api(f"/x{self.comId}/s/chat/thread/{chatId}/admin")
        else: raise TypeError("Please put a wiki or user or chat or blog Id")

        data = {
            "adminOpNote": {"content": note},
            "adminOpName": opN,
            "adminOpValue": opV,
            "timestamp": int(timestamp() * 1000)
        }

        req = requests.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def send_warning(self, userId: str, reason: str = None):
        data = json.dumps({
            "uid": userId,
            "title": "Custom",
            "content": reason,
            "attachedObject": {"objectId": userId,"objectType": 0},
            "penaltyType": 0,
            "adminOpNote": {},
            "noticeType": 7,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/notice"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_to_voice_chat(self, userId: str = None, chatId: str = None):
        data = json.dumps({"uid": userId, "timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/g/x{self.comId}/chat/thread/{chatId}/vvchat-presenter/invite"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def post_blog(self, title: str, content: str, fansOnly: bool = False):
        data = {
            "extensions": {"fansOnly": fansOnly},
            "content": content,
            "latitude": 0,
            "longitude": 0,
            "title": title,
            "type": 0,
            "contentLanguage": "ar",
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }
        data = json.dumps(data)

        req = requests.post(api(f"/x{self.comId}/s/blog"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def post_wiki(self, title: str, content: str, fansOnly: bool = False, icon: str = None, backgroundColor: str = None, keywords: [str, list] = None):
        data = {
            "extensions": {"fansOnly": fansOnly, "props": [], "style": {"backgroundColor": backgroundColor}},
            "content": content,
            "keywords": keywords,
            "label": title,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        }
        if icon: data["icon"] = icon

        data = json.dumps(data)
        req = requests.post(api(f"/x{self.comId}/s/item"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_blog(self, blogId: str):
        req = requests.delete(api(f"/x{self.comId}/s/blog/{blogId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_wiki(self, wikiId: str):
        req = requests.delete(api(f"/x{self.comId}/s/item/{wikiId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def activate_status(self, status: int = 1):
        data = json.dumps({"onlineStatus": status,"duration": 86400,"timestamp": int(timestamp() * 1000)})
        req = requests.post(api(f"/x{self.comId}/s/user-profile/{self.uid}/online-status"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(os.urandom(16)).decode("ascii")))
        data = json.dumps({
            "paymentContext": {
                "transactionId": transactionId,
                "isAutoRenew": autoRenew
            },
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/influencer/{userId}/subscribe"), data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def submit_wiki(self, wikiId: str, message: str = None):
        data = {
            "message": message,
            "itemId": wikiId,
            "timestamp": int(timestamp() * 1000)
        }
        data = json.dumps(data)
        req = requests.post(api(f"/x{self.comId}/s/knowledge-base-request"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def edit_blog(self, title: str, content: str, blogId: str = None, wikiId: str = None, fansOnly: bool = False, backgroundColor: str = None):
        data = {
            "title": title,
            "content": content,
            "timestamp": int(timestamp() * 1000)
        }

        if fansOnly: data["extensions"]["fansOnly"] = True
        if backgroundColor: data["extensions"] = {"backgroundColor": backgroundColor}
        if blogId: url = api(f"/x{self.comId}/s/blog/{blogId}")
        elif wikiId: url = api(f"/x{self.comId}/s/item/{wikiId}")
        else: raise TypeError("Please put blogId or wikiId")

        data = json.dumps(data)
        req = requests.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_chat_bubbles(self, start: int = 0, size: int = 20):
        req = requests.get(api(f"/x{self.comId}/s/chat/chat-bubble?type=all-my-bubbles&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return BubbleList(req.json()["chatBubbleList"]).BubbleList

    def select_bubble(self, bubbleId: str, apply: int = 0, chatId: str = None):
        data = {"bubbleId": bubbleId, "applyToAll": apply, "timestamp": int(timestamp() * 1000)}
        if chatId: data["threadId"] = chatId
        data = json.dumps(data)
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/apply-bubble"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def delete_chat_bubble(self, bubbleId: str):
        req = requests.delete(url=api(f"/x{self.comId}/s/chat/chat-bubble/{bubbleId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def get_chat_bubble_templates(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/x{self.comId}/s/chat/chat-bubble/templates?start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return BubbleTemplates(req.json()["templateList"])

    def upload_custom_bubble(self, templateId: str, bubble: BinaryIO):
        req = requests.post(api(f"/x{self.comId}/s/chat/chat-bubble/templates/{templateId}/generate"), headers=self.headers, proxies=self.proxies, data=bubble)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def kick(self, chatId: str, userId: str, rejoin: bool = True):
        if rejoin: rejoin = 1
        if not rejoin: rejoin = 0

        req = requests.delete(api(f"/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={rejoin}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def web_active_time(self):
        try:
            data = {"ndcId": self.comId}
            req = requests.post("https://aminoapps.com/api/community/stats/web-user-active-time", json=data, headers=self.web_headers)
            try:
                if req.json()["code"] != 200: return CheckExceptions(req.json())
                else: Json(req.json())
            except: return CheckExceptions(req.json())
            return Json(req.json())
        except: raise Exception("Unknown error")

    def block(self, userId: str):
        req = requests.post(api(f"/x{self.comId}/s/block/{userId}"), headers=self.headers, proxies=self.proxies)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def send_active_time(self, startTime: int = None, endTime: int = None, optInAdsFlags: int = 2147483647, tz: int = -timezone // 1000, timers: list = None, timestamp: int = int(timestamp() * 1000)):
        data = {
            "userActiveTimeChunkList": [{"start": startTime, "end": endTime}],
            "timestamp": timestamp,
            "optInAdsFlags": optInAdsFlags,
            "timezone": tz
        }
        if timers: data["userActiveTimeChunkList"] = timers

        data = json_minify(json.dumps(data))
        req = requests.post(api(f"/x{self.comId}/s/community/stats/user-active-time"), headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def transfer_host(self, chatId: str, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer"), headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())

    def accept_host(self, chatId: str, requestId: str):
        data = json.dumps({})
        req = requests.post(api(f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept"), headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        else: return Json(req.json())
