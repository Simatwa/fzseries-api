import click
import os
import fzseries_api


search_filters: list[str] = [
    "IMDBTop250Filter",
    "PopularityFilter",
    "AiredTodayFilter",
    "TrendingFilter",
    "FreshSeriesFilter",
    "TopRatedMiniseriesFilter",
    "NetflixOriginalFilter",
    "NetflixOriginalFilter",
    "HBOOriginalFilter",
    "CartoonFilter",
    "GenreFilter",
    "AlphabeticalOrderFilter ",
]


@click.group(epilog=f"Repository : {fzseries_api.__repo__}")
@click.version_option(version=fzseries_api.__version__)
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
        help="Number of trials before giving up on downloading an episode",
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
    @click.option(
        "--confirm", is_flag=True, help="Confirm episodes before downloading them"
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
        confirm,
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
            confirm=confirm,
        )

    @click.command()
    @click.argument("query")
    @click.option(
        "-s", "--season", type=click.INT, help="Show metadata for a particular season"
    )
    @click.option("--seasons-only", is_flag=True, help="Show seasons information only")
    def metadata(query, season: int, seasons_only: bool):
        """Access particular series metadata - seasons and episodes"""
        import rich
        from rich.table import Table
        from fzseries_api import Search, TVSeriesMetadata, EpisodeMetadata

        results = Search(query).results
        tvseries_metadata = TVSeriesMetadata(results.series[0]).results
        seasons = tvseries_metadata.seasons
        if seasons_only:
            seasons_table = Table(
                show_lines=True, title=f"{tvseries_metadata.title} Seasons".title()
            )
            seasons_table.add_column("Number", justify="center", style="yellow")
            seasons_table.add_column("Season", justify="left", style="cyan")
            for current_season in seasons:
                seasons_table.add_row(
                    str(current_season.number), current_season.identity
                )
            rich.print(seasons_table)
            return

        for index, target_season in enumerate(seasons):
            if seasons_only:
                break
            if season and not target_season.number == season:
                continue
            episode_metadata = EpisodeMetadata(target_season).results
            season_table = Table(
                show_lines=True,
                title=f"{tvseries_metadata.title} {target_season.identity} Metadata".title(),
            )
            season_table.add_column("No.", justify="center", style="yellow")
            season_table.add_column("Title", justify="left", style="cyan")
            season_table.add_column("Date Aired", justify="left", style="yellow")
            season_table.add_column("About", justify="left", style="yellow")
            season_table.add_column("Stars", justify="left", style="yellow")
            season_table.add_column("Director", justify="left", style="yellow")
            season_table.add_column("Writer", justify="left", style="yellow")

            for count, episode in enumerate(episode_metadata.episodes, start=1):
                season_table.add_row(
                    str(count),
                    episode.title,
                    episode.aired_on.strftime("%d-%b-%Y"),
                    episode.about,
                    episode.stars,
                    episode.director,
                    episode.writer,
                )
            rich.print(season_table)

    @click.command()
    @click.argument("query", required=False)
    @click.option(
        "-f",
        "--filter",
        help="Perform search using filters",
        metavar="|".join(search_filters[:3]) + "...",
        type=click.Choice(search_filters),
    )
    @click.option("-v", "--value", help="Filter argument")
    @click.option(
        "-l",
        "--limit",
        help="Search results limit",
        type=click.INT,
        default=1000000,
    )
    @click.option("--all", is_flag=True, help="Show all search results")
    def discover(query: str, filter: str, value: str, limit: int, all: bool):
        """Search TV series using title or filter"""
        from fzseries_api import Search
        from fzseries_api.filters import (
            IMDBTop250Filter,
            PopularityFilter,
            AiredTodayFilter,
            TrendingFilter,
            FreshSeriesFilter,
            TopRatedMiniseriesFilter,
            NetflixOriginalFilter,
            NetflixOriginalFilter,
            HBOOriginalFilter,
            CartoonFilter,
            GenreFilter,
            AlphabeticalOrderFilter,
            fzseriesFilterType,
        )

        filters_obj: list[fzseriesFilterType] = [
            IMDBTop250Filter,
            PopularityFilter,
            AiredTodayFilter,
            TrendingFilter,
            FreshSeriesFilter,
            TopRatedMiniseriesFilter,
            NetflixOriginalFilter,
            NetflixOriginalFilter,
            HBOOriginalFilter,
            CartoonFilter,
            GenreFilter,
            AlphabeticalOrderFilter,
        ]
        if query:
            search = Search(query)
        elif filter:
            filter_str_obj_map: dict[str, object] = dict(
                zip(search_filters, filters_obj)
            )
            filter_obj: fzseriesFilterType = filter_str_obj_map.get(filter)

            if filter_obj.init_with_args:
                if not value:
                    raise Exception(
                        f'Filter "{filter}" requires an argument. Use -v / --value '
                        "to pass the required argument."
                    )
                search = Search(query=filter_obj(value))
            else:
                if value:
                    raise Exception(f'Filter "{filter}" does not require an argument.')
                search = Search(filter_obj())
        else:
            raise Exception("A search must be performed with a QUERY or a FILTER!")

        import rich
        from rich.table import Table

        results = search.results
        page_count = index_count = 0
        for results in search.get_all_results(stream=True, limit=limit):
            page_count += 1
            search_results_table = Table(
                show_lines=True,
                title=f"Search Results - {filter if filter else query} {'('+value+')' if value else ''} Pg. {page_count}".title(),
            )
            search_results_table.add_column("Index", justify="center", style="yellow")
            search_results_table.add_column("Title", justify="left", style="cyan")
            search_results_table.add_column("About", justify="left", style="yellow")
            for series in results.series:
                index_count += 1
                search_results_table.add_row(
                    str(index_count), series.title, series.about
                )
            rich.print(search_results_table)
            if not all:
                break


class Utils:
    """Utility commands"""

    @staticmethod
    @click.command()
    @click.argument(
        "domain",
        type=click.Choice(
            [
                "https://tvseries.in/",
                "https://mobiletvshows.site/",
                "https://fztvseries.live/",
            ]
        ),
    )
    def set_domain(domain):
        """Set domain for making requests to"""
        #    f'export FZSERIES_DEFAULT_SITE="{domain}"'
        raise NotImplementedError("Function not yet implemented")


class EntryGroup:
    """Click command groups"""

    @staticmethod
    @fzseries.group()
    def utils():
        """Utility commands for fzseries"""
        pass


def main():
    """Console entrypoint"""
    try:
        fzseries.add_command(Commands.download)
        fzseries.add_command(Commands.metadata)
        fzseries.add_command(Commands.discover)
        EntryGroup.utils.add_command(Utils.set_domain)
        fzseries()
    except Exception as e:
        click.secho(
            f"Error occured - {e.args[1] if e.args and len(e.args)>1 else e}"
            "\nQuitting.",
            color="yellow",
        )


if __name__ == "__main__":
    main()
