import asyncio

from src.modules.media.sources.domain.dtos import (
    DownloadedFile,
    DownloadItem,
    DownloadProcessRequest,
)
from src.modules.media.sources.infra.downloaders.direct import DirectDownloader
from src.modules.media.sources.infra.downloaders.hls import HLSMP3Downloads
from src.modules.media.sources.infra.downloaders.native import (
    NativeMediaMetadata,
)
from src.modules.media.sources.infra.metadata import MediaMetadataExtraction
from src.modules.media.sources.infra.threads import MediaMetadataThreads
from src.modules.media.sources.infra.transfer import MediaFileTransfer
from src.modules.media.sources.interfaces import (
    IYoutubeSourceResolver,
)


class MediaSourceTransfer:
    def __init__(
        self,
        metadata: MediaMetadataExtraction,
        transfer: MediaFileTransfer,
        youtube: IYoutubeSourceResolver,
        threads: MediaMetadataThreads,
    ):
        self.metadata = metadata
        self.transfer = transfer
        self.youtube = youtube
        self.threads = threads

    async def download(
        self, request: DownloadProcessRequest, item: DownloadItem
    ) -> DownloadedFile:
        native = NativeMediaMetadata(request, self.threads)
        result = (
            await HLSMP3Downloads(request, native).download(item)
            if item.transport == "hls_mp3"
            else await DirectDownloader(request, native).download(item)
        )
        return result

    async def fetch(self, request: DownloadProcessRequest) -> DownloadedFile:
        if request.item is None:
            raise ValueError("Download item is required")
        if request.item.engine == "spotify":
            raise ValueError(
                "Direct Spotify audio is unavailable; "
                "substitute sources are disabled"
            )
        if request.item.engine in {"youtube", "soundcloud"}:
            async with asyncio.timeout(request.policy.item_timeout_seconds):
                if request.item.engine == "soundcloud":
                    resolved = await self.metadata.resolve(
                        request, request.item
                    )
                    item = resolved.item
                else:
                    item = await self.youtube.resolve(request, request.item)
                try:
                    result = await self.download(request, item)
                except Exception as primary_error:
                    if (
                        request.item.engine != "youtube"
                        or item.engine != "youtube"
                        or not request.policy.youtube_api_url
                    ):
                        raise
                    fallback = request.model_copy(
                        update={
                            "policy": request.policy.model_copy(
                                update={"youtube_api_url": None}
                            )
                        }
                    )
                    try:
                        item = await self.youtube.resolve(
                            fallback, request.item
                        )
                        if request.item.duration is not None:
                            item = item.model_copy(
                                update={"duration": request.item.duration}
                            )
                        result = await self.download(fallback, item)
                    except Exception as fallback_error:
                        raise ValueError(
                            "YouTube API transfer failed: "
                            + str(primary_error)[:150]
                            + "; direct source failed: "
                            + str(fallback_error)[:220]
                        ) from fallback_error
        else:
            result = await self.transfer.fetch(request)
        return result
