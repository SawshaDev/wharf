from __future__ import annotations


class Asset:
    BASE_URL = "https://cdn.discordapp.com"

    def __init__(self, *, url: str, key: str, animated: bool = False):
        self._url: str = url
        self._animated: bool = animated
        self._key: str = key

    @property
    def url(self) -> str:
        """:class:`str`: Returns the underlying URL of the asset."""
        return self._url

    @property
    def key(self) -> str:
        """:class:`str`: Returns the identifying key of the asset."""
        return self._key

    def is_animated(self) -> bool:
        """:class:`bool`: Returns whether the asset is animated."""
        return self._animated

    @classmethod
    def _from_avatar(cls, user_id: int, avatar: str):
        animated = avatar.startswith("a_")
        formatted = "gif" if animated else "png"
        return cls(
            url=f"{cls.BASE_URL}/avatars/{user_id}/{avatar}.{formatted}?size=1024",
            key=avatar,
            animated=animated,
        )


    @classmethod
    def _from_user_banner(cls, user_id: int, banner_hash: str):
        animated = banner_hash.startswith('a_')
        format = 'gif' if animated else 'png'
        return cls(
            url=f'{cls.BASE_URL}/banners/{user_id}/{banner_hash}.{format}?size=512',
            key=banner_hash,
            animated=animated,
        )