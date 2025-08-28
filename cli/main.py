import json
import click
from looptube.entities import Video, Channel, Playlist
from looptube.utils import LocalClient

local_client = LocalClient()


@click.group(name="looptube")
def looptube():
    """Top-Level Commands for Looptube"""
    pass


@looptube.command(
    name="vtest",
    help="Run a Visual Browser Test for one of Video, Channel, or Playlist",
)
@click.argument(
    "entity",
    type=click.Choice(["video", "channel", "playlist"]),
    required=True,
)
@click.argument(
    "url",
    type=str,
    required=True,
)
def vtest(entity: str, url: str):
    if entity == "video":
        model = type(f"TestVideo", (Video,), dict(__headless__=False))
    elif entity == "channel":
        model = type(f"TestChannel", (Channel,), dict(__headless__=False))
    elif entity == "playlist":
        model = type(f"TestPlaylist", (Playlist,), dict(__headless__=False))
    data = model(url)
    click.echo(json.dumps(data.to_json(), indent=4))



yt_ent_dwn_opts = click.option(
    "--download",
    "-d",
    is_flag=True,
    default=False,
    help="Download Video or Audio file(s)",
)
yt_ent_aud_opts = click.option(
    "--audio",
    "-a",
    is_flag=True,
    default=False,
    help="Download only audio file(s)",
)
yt_ent_sum_opts = click.option(
    "--summarize",
    "-s",
    is_flag=True,
    default=False,
    help="Summarize the Video and/or Audio File(s)",
)
yt_ent_tb_opts = click.option(
    "--transcribe",
    "-tb",
    is_flag=True,
    default=False,
    help="Transcribe the Video and/or Audio File(s)",
)
yt_ent_tr_opts = click.option(
    "--translate",
    "-tr",
    is_flag=True,
    default=False,
    help="Translate the Video and/or Audio File(s)",
)
yt_ent_emb_opts = click.option(
    "--embed",
    "-e",
    is_flag=True,
    default=False,
    help="Embed the Video and/or Audio File(s)",
)


@looptube.command(
    name="video",
    help="ML and AI tasks for YouTube Videos",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.argument("vid", type=str, required=True)
@yt_ent_dwn_opts
@yt_ent_aud_opts
@yt_ent_sum_opts
@yt_ent_tb_opts
@yt_ent_tr_opts
@yt_ent_emb_opts
def video(
    vid: str,
    download: bool,
    audio: bool,
    summarize: bool,
    transcribe: bool,
    translate: bool,
    embed: bool,
):
    url = vid if vid.startswith("https://") else f"https://www.youtube.com/watch?v={vid}"
    click.echo(f"Fetching video from {url}")
        
    click.echo(json.dumps(Video.__schema__.mock_me(url=url).model_dump(mode="json"), indent=4))



@looptube.command(
    name="channel",
    help="ML and AI tasks for YouTube Channels",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.argument("cid", type=str, required=True)
@yt_ent_dwn_opts
@yt_ent_aud_opts
@yt_ent_sum_opts
@yt_ent_tr_opts
@yt_ent_tr_opts
@yt_ent_emb_opts
def channel(
    cid: str,
    download: bool,
    audio: bool,
    summarize: bool,
    transcribe: bool,
    translate: bool,
    embed: bool,
):
    url = cid if cid.startswith("https://") else f"https://www.youtube.com/channel/{cid}"
    click.echo(f"Fetching channel from {url}")
    click.echo(json.dumps(Channel.__schema__.mock_me(url=url).model_dump(mode="json"), indent=4))


@looptube.command(
    name="playlist",
    help="ML and AI tasks for YouTube Playlists",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.argument("plid", type=str, required=True)
@yt_ent_dwn_opts
@yt_ent_aud_opts
@yt_ent_sum_opts
@yt_ent_tb_opts
@yt_ent_tr_opts
@yt_ent_emb_opts
def playlist(
    plid: str,
    download: bool,
    audio: bool,
    summarize: bool,
    transcribe: bool,
    translate: bool,
    embed: bool,
):
    url = plid if plid.startswith("https://") else f"https://www.youtube.com/playlist?list={plid}"
    click.echo(f"Fetching playlist from {url}")
    click.echo(json.dumps(Playlist.__schema__.mock_me(url=url).model_dump(mode="json"), indent=4))


if __name__ == "__main__":
    looptube()
