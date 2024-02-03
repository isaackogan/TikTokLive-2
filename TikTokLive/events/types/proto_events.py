# Generated by the TikTokLive compiler.
# DO NOT EDIT!
# SERIOUSLY!
# I MEAN IT!

from typing import Dict, Type, Union
from TikTokLive.proto import *
from ...events.event import BaseEvent
from typing import Type, Union

class CommentEvent(BaseEvent, WebcastChatMessage):
    """
    CommentEvent
    """



class BarrageEvent(BaseEvent, WebcastBarrageMessage):
    """
    BarrageEvent
    """


class CaptionEvent(BaseEvent, WebcastCaptionMessage):
    """
    CaptionEvent
    """


class ControlEvent(BaseEvent, WebcastControlMessage):
    """
    ControlEvent
    """


class EmoteChatEvent(BaseEvent, WebcastEmoteChatMessage):
    """
    EmoteChatEvent
    """


class EnvelopeEvent(BaseEvent, WebcastEnvelopeMessage):
    """
    EnvelopeEvent
    """


class GiftEvent(BaseEvent, WebcastGiftMessage):
    """
    GiftEvent
    """


class GoalUpdateEvent(BaseEvent, WebcastGoalUpdateMessage):
    """
    GoalUpdateEvent
    """


class HourlyRankEvent(BaseEvent, WebcastHourlyRankMessage):
    """
    HourlyRankEvent
    """


class ImDeleteEvent(BaseEvent, WebcastImDeleteMessage):
    """
    ImDeleteEvent
    """


class LikeEvent(BaseEvent, WebcastLikeMessage):
    """
    LikeEvent
    """


class LinkEvent(BaseEvent, WebcastLinkMessage):
    """
    LinkEvent
    """


class LinkLayerEvent(BaseEvent, WebcastLinkLayerMessage):
    """
    LinkLayerEvent
    """


class LinkMicArmies(BaseEvent, WebcastLinkMicArmies):
    """
    LinkMicArmies
    """


class LinkMicBattle(BaseEvent, WebcastLinkMicBattle):
    """
    LinkMicBattle
    """


class LinkMicFanTicketMethod(BaseEvent, WebcastLinkMicFanTicketMethod):
    """
    LinkMicFanTicketMethod
    """


class LinkMicMethod(BaseEvent, WebcastLinkMicMethod):
    """
    LinkMicMethod
    """


class LiveIntroEvent(BaseEvent, WebcastLiveIntroMessage):
    """
    LiveIntroEvent
    """


class MemberEvent(BaseEvent, WebcastMemberMessage):
    """
    MemberEvent
    """


class MessageDetectEvent(BaseEvent, WebcastMsgDetectMessage):
    """
    MessageDetectEvent
    """


class OecLiveShoppingEvent(BaseEvent, WebcastOecLiveShoppingMessage):
    """
    OecLiveShoppingEvent
    """


class PollEvent(BaseEvent, WebcastPollMessage):
    """
    PollEvent
    """


class QuestionNewEvent(BaseEvent, WebcastQuestionNewMessage):
    """
    QuestionNewEvent
    """


class RankTextEvent(BaseEvent, WebcastRankTextMessage):
    """
    RankTextEvent
    """


class RankUpdateEvent(BaseEvent, WebcastRankUpdateMessage):
    """
    RankUpdateEvent
    """


class RoomEvent(BaseEvent, WebcastRoomMessage):
    """
    RoomEvent
    """


class RoomPinEvent(BaseEvent, WebcastRoomPinMessage):
    """
    RoomPinEvent
    """


class RoomUserSeqEvent(BaseEvent, WebcastRoomUserSeqMessage):
    """
    RoomUserSeqEvent
    """


class SocialEvent(BaseEvent, WebcastSocialMessage):
    """
    SocialEvent
    """


class SubNotifyEvent(BaseEvent, WebcastSubNotifyMessage):
    """
    SubNotifyEvent
    """


class SystemEvent(BaseEvent, WebcastSystemMessage):
    """
    SystemEvent
    """


class UnauthorizedMemberEvent(BaseEvent, WebcastUnauthorizedMemberMessage):
    """
    UnauthorizedMemberEvent
    """


EVENT_MAPPINGS: Dict[str, BaseEvent] = {
    "WebcastGiftMessage": GiftEvent,
    "WebcastRoomMessage": RoomEvent,
    "WebcastBarrageMessage": BarrageEvent,
    "WebcastCaptionMessage": CaptionEvent,
    "WebcastChatMessage": CommentEvent,
    "WebcastControlMessage": ControlEvent,
    "WebcastEmoteChatMessage": EmoteChatEvent,
    "WebcastEnvelopeMessage": EnvelopeEvent,
    "WebcastGoalUpdateMessage": GoalUpdateEvent,
    "WebcastImDeleteMessage": ImDeleteEvent,
    "WebcastLikeMessage": LikeEvent,
    "WebcastRoomUserSeqMessage": RoomUserSeqEvent,
    "WebcastSocialMessage": SocialEvent,
    "WebcastSubNotifyMessage": SubNotifyEvent,
    "WebcastRankUpdateMessage": RankUpdateEvent,
    "WebcastMemberMessage": MemberEvent,
    "WebcastPollMessage": PollEvent,
    "WebcastQuestionNewMessage": QuestionNewEvent,
    "WebcastRankTextMessage": RankTextEvent,
    "WebcastHourlyRankMessage": HourlyRankEvent,
    "WebcastLinkMicArmies": LinkMicArmies,
    "WebcastLinkMicBattle": LinkMicBattle,
    "WebcastLinkMicFanTicketMethod": LinkMicFanTicketMethod,
    "WebcastLinkMicMethod": LinkMicMethod,
    "WebcastLiveIntroMessage": LiveIntroEvent,
    "WebcastUnauthorizedMemberMessage": UnauthorizedMemberEvent,
    "WebcastMsgDetectMessage": MessageDetectEvent,
    "WebcastOecLiveShoppingMessage": OecLiveShoppingEvent,
    "WebcastRoomPinMessage": RoomPinEvent,
    "WebcastSystemMessage": SystemEvent,
    "WebcastLinkMessage": LinkEvent,
    "WebcastLinkLayerMessage": LinkLayerEvent,
}

ProtoEvent: Type = Union[
    WebcastGiftMessage,
    WebcastRoomMessage,
    WebcastBarrageMessage,
    WebcastCaptionMessage,
    WebcastChatMessage,
    WebcastControlMessage,
    WebcastEmoteChatMessage,
    WebcastEnvelopeMessage,
    WebcastGoalUpdateMessage,
    WebcastImDeleteMessage,
    WebcastLikeMessage,
    WebcastRoomUserSeqMessage,
    WebcastSocialMessage,
    WebcastSubNotifyMessage,
    WebcastRankUpdateMessage,
    WebcastMemberMessage,
    WebcastPollMessage,
    WebcastQuestionNewMessage,
    WebcastRankTextMessage,
    WebcastHourlyRankMessage,
    WebcastLinkMicArmies,
    WebcastLinkMicBattle,
    WebcastLinkMicFanTicketMethod,
    WebcastLinkMicMethod,
    WebcastLiveIntroMessage,
    WebcastUnauthorizedMemberMessage,
    WebcastMsgDetectMessage,
    WebcastOecLiveShoppingMessage,
    WebcastRoomPinMessage,
    WebcastSystemMessage,
    WebcastLinkMessage,
    WebcastLinkLayerMessage,
]

__all__ = [
    "GiftEvent",
    "RoomEvent",
    "BarrageEvent",
    "CaptionEvent",
    "CommentEvent",
    "ControlEvent",
    "EmoteChatEvent",
    "EnvelopeEvent",
    "GoalUpdateEvent",
    "ImDeleteEvent",
    "LikeEvent",
    "RoomUserSeqEvent",
    "SocialEvent",
    "SubNotifyEvent",
    "RankUpdateEvent",
    "MemberEvent",
    "PollEvent",
    "QuestionNewEvent",
    "RankTextEvent",
    "HourlyRankEvent",
    "LinkMicArmies",
    "LinkMicBattle",
    "LinkMicFanTicketMethod",
    "LinkMicMethod",
    "LiveIntroEvent",
    "UnauthorizedMemberEvent",
    "MessageDetectEvent",
    "OecLiveShoppingEvent",
    "RoomPinEvent",
    "SystemEvent",
    "LinkEvent",
    "LinkLayerEvent",
    "EVENT_MAPPINGS",
    "ProtoEvent"
]
