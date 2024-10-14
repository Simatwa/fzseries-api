import click
import os


@click.group(epilog="This script has no any official relation with fztseries.live")
def fzseries():
    """Unofficial Python SDK/API for fztvseries.live"""
    pass


class Commands:

    @staticmethod
    @click.command()
    @click.argument("query")
    @click.option(
        "-b",
        "--by",
        help="Query category",
        type=click.Choice(["series", "episodes"]),
        default="series",
    )
    @click.option(
        "-so",
        "--season-offset",
        type=click.INT,
        help="Season number to start downloading from",
        default=1,
    )
    @click.option(
        "-eo",
        "--episode-offset",
        type=click.INT,
        help="Episode number to start downloading from",
        default=1,
    )
    @click.option(
        "-l",
        "--limit",
        type=click.INT,
        default=1000000,
        help="Number of proceeding episodes to download before stopping",
    )
    @click.option(
        "-t",
        "--download-trials",
        type=click.INT,
        help="Number of trials before giving up on download",
        default=10,
    )
    @click.option(
        "-r",
        "--request-timeout",
        type=click.INT,
        help="Http request timeout while downloading episodes in seconds.",
        default=30 * 60,
    )
    @click.option(
        "-f",
        "--format",
        type=click.Choice(["High MP4", "WEBM"]),
        default="High MP4",
        help="Preffered movie download format",
    )
    @click.option(
        "-d",
        "--directory",
        default=os.getcwd(),
        help="Parent directory for saving the downloaded contents",
        type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    )
    @click.option(
        "--enable-progressbar/--disable-progressbar",
        default=True,
        help="Show or hide downloading progress bar",
    )
    @click.option(
        "--quiet", is_flag=True, help="Do not stdout any interactive messages"
    )
    @click.option(
        "--include_metadata",
        is_flag=True,
        help="Add series title and episode-id in filename",
    )
    @click.option(
        "--one-season-only", is_flag=True, help="Download only one season and stop."
    )
    @click.option(
        "--ignore-errors",
        is_flag=True,
        help="Ignore exceptions raised while downloading episode",
    )
    def download(
        query,
        by,
        season_offset,
        episode_offset,
        limit,
        download_trials,
        request_timeout,
        format,
        directory,
        enable_progressbar,
        quiet,
        include_metadata,
        one_season_only,
        ignore_errors,
    ):
        """Download a whole series|seasons|episodes automatically"""
        from fzseries_api import Auto

        auto = Auto(query=query, by=by)
        auto.run(
            season_offset=season_offset,
            episode_offset=episode_offset,
            one_season_only=one_season_only,
            ignore_errors=ignore_errors,
            limit=limit,
            download_trials=download_trials,
            timeout=request_timeout,
            format=format,
            directory=directory,
            progress_bar=enable_progressbar,
            quiet=quiet,
            include_metadata=include_metadata,
        )


def main():
    """Console entrypoint"""
    fzseries.add_command(Commands.download)
    fzseries()


if __name__ == "__main__":
    main()
