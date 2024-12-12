class EscapeRoomError(Exception):
    """base exception class"""

    def __init__(self, message="User already owns this story.", name="EscapeRoom"):
        self.message = message
        self.name = name
        super().__init__(self.message)


class ServiceError(EscapeRoomError):
    """generic error"""

    pass


class StoryAlreadyOwnedError(EscapeRoomError):
    """Story already bought for this user"""

    pass


class StoryAlreadyStartedError(EscapeRoomError):
    """Story already bought for this user"""

    pass


class InsufficientGoldError(EscapeRoomError):
    """Not enough gold for purchase the story"""

    pass


class EntityDoesNotExistError(EscapeRoomError):
    """Not enough gold for purchase the story"""

    pass


class UnAuthenticatedUserError(EscapeRoomError):
    """Not enough gold for purchase the story"""

    pass


class EmptyPasswordFormError(EscapeRoomError):
    """Not enough gold for purchase the story"""

    pass
