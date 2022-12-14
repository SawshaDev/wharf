from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .impl import Cache


class Asset:
    BASE_URL = "https://cdn.discordapp.com"

    def __init__(self, *, url: str, key: str, animated: bool = False, cache: "Cache"):
        self.cache = cache
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
    def _from_avatar(cls, user_id: int, avatar: str, cache: Cache):
        animated = avatar.startswith("a_")
        formatted = "gif" if animated else "png"
        return cls(
            url=f"{cls.BASE_URL}/avatars/{user_id}/{avatar}.{formatted}?size=1024",
            key=avatar,
            animated=animated,
            cache=cache
        )

    @classmethod
    def _from_user_banner(cls, user_id: int, banner_hash: str, cache: Cache):
        animated = banner_hash.startswith("a_")
        format = "gif" if animated else "png"
        return cls(
            url=f"{cls.BASE_URL}/banners/{user_id}/{banner_hash}.{format}?size=512",
            key=banner_hash,
            animated=animated,
            cache=cache
        )

    @classmethod
    def _from_guild_icon(cls, cache: Cache, guild_id: int, icon_hash: str):
        animated = icon_hash.startswith('a_')
        format = 'gif' if animated else 'png'
        return cls(
            cache=cache,
            url=f'{cls.BASE_URL}/icons/{guild_id}/{icon_hash}.{format}?size=1024',
            key=icon_hash,
            animated=animated,
        )

    @classmethod
    def _from_guild_image(cls, cache: Cache, guild_id: int, image: str, path: str):
        animated = image.startswith('a_')
        format = 'gif' if animated else 'png'
        return cls(
            cache=cache,
            url=f'{cls.BASE_URL}/{path}/{guild_id}/{image}.{format}?size=1024',
            key=image,
            animated=animated,
        )

    async def read(self):
        return await self.cache.http.read_from_cdn(self._url)