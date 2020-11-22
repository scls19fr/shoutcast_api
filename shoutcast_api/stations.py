from requests.sessions import session
from shoutcast_api import shoutcast_request
from typing import Tuple, AnyStr, List
from .models import Station, StationList
from .utils import _build_url, station_xml_strip, station_json_strip


def _handle_url_action_xml(endpoint: str, session):
    stations = list()
    response = shoutcast_request.call_api_xml(endpoint, session=session)
    api_station_list = response.get('stationlist')

    if not api_station_list.get('station'):
        return StationList(tunein=shoutcast_request.tuneins, stations=[])

    api_stations = api_station_list.get('station')
    if not isinstance(api_stations, list):
        return StationList(tunein=shoutcast_request.tuneins, stations=[Station(station_xml_strip(api_stations))])

    for item in api_stations:
        stations.append(Station(station_xml_strip(item)))

    return StationList(tunein=shoutcast_request.tuneins, stations=stations)


def _handle_url_action_json(endpoint: str, session) -> StationList:
    stations = list()
    response = shoutcast_request.call_api_json(endpoint, session=session)
    api_station_list = response.get('stationlist')

    if not api_station_list.get('station'):
        return StationList(tunein=shoutcast_request.tuneins, stations=[])

    api_stations = api_station_list.get('station')
    if not isinstance(api_stations, list):
        return StationList(tunein=shoutcast_request.tuneins, stations=[Station(station_json_strip(api_stations))])

    for item in api_stations:
        stations.append(Station(station_json_strip(item)))

    return StationList(tunein=shoutcast_request.tuneins, stations=stations)


def get_top_500(k: AnyStr, limit: (int, Tuple) = None, session=None, **kwargs) -> StationList:
    """
    gets top 500 stations from shoutcast api
    :param k: API Dev Key.
    :param limit: limit the number of stations to return by passing the limit parameter. for example
    `limit=(X,Y)` - Y is the number of results to return and X is the offset.
    :param kwargs:
        br - Filter the stations based on bitrate specified.
        mt - Filter the stations based on media type specified, MP3 = audio/mpeg and AAC+ = audio/aacp
    :return: list of stations
    """

    endpoint = '/legacy/Top500?k={}'.format(k)
    endpoint += _build_url(limit=limit, **kwargs)

    return _handle_url_action_xml(endpoint, session=session)


def get_stations_keywords(k, search: str, limit: (int, Tuple) = None, session=None, **kwargs) -> StationList:
    """
        Get stations which match the keyword searched on SHOUTcast Radio Directory.
       :param search: Specify the query to search
       :param k: API Dev Key.
       :param limit: limit the number of stations to return by passing the limit parameter. for example
       `limit=(X,Y)` - Y is the number of results to return and X is the offset.
       :param kwargs:
           br - Filter the stations based on bitrate specified.
           mt - Filter the stations based on media type specified, MP3 = audio/mpeg and AAC+ = audio/aacp
       :return: `List[Stations]`
    """
    if not search:
        raise Exception('Search query is required')

    endpoint = "/legacy/stationsearch?k={}&search={}".format(k, search.replace(' ', '+').strip())
    endpoint += _build_url(limit, **kwargs)

    return _handle_url_action_xml(endpoint, session=session)


def get_stations_by_genre(k, genre: str, limit: (int, Tuple) = None, session=None, **kwargs) -> StationList:
    """
       Get stations which match the genre specified as query.
       :param genre: genre
       :param k: API Dev Key.
       :param limit: limit the number of stations to return by passing the limit parameter. for example
      `limit=(X,Y)` - Y is the number of results to return and X is the offset.
       :param kwargs:
           br - Filter the stations based on bitrate specified.
           mt - Filter the stations based on media type specified, MP3 = audio/mpeg and AAC+ = audio/aacp
       :return: `List[Stations]`
    """
    if not genre:
        raise Exception('genre is required')

    endpoint = "/legacy/stationsearch?k={}&search={}".format(
        k, genre.replace(' ', '+').strip()
    )
    endpoint += _build_url(limit, **kwargs)

    return _handle_url_action_xml(endpoint, session=session)


def get_stations_by_now_playing(k, ct: str, limit: (int, Tuple) = None, session=None, **kwargs) -> StationList:
    """
       Return stations which match a specified query in the now playing node.
       :param ct: Query to search in Now Playing node. This parameter also supports querying multiple artists in the same query by using "||". ex: ct=madonna||u2||beyonce up to 10 artists
       :param k: API Dev Key.
       :param limit: limit the number of stations to return by passing the limit parameter. for example
       `limit=(X,Y)` - Y is the number of results to return and X is the offset.
       :param kwargs:
           br - Filter the stations based on bitrate specified.
           mt - Filter the stations based on media type specified, MP3 = audio/mpeg and AAC+ = audio/aacp
       :return: `List[Stations]`
    """
    if not ct:
        raise Exception('genre is required')

    endpoint = "/station/nowplaying?k={}&ct={}&f=json".format(
        k, ct.replace(' ', '+').strip()
    )
    endpoint += _build_url(limit, **kwargs)

    return _handle_url_action_json(endpoint, session=session)


def get_stations_bitrate_or_genre_id(k, br: int = 128,
                                     genre_id: int = None, limit: (int, Tuple) = None, session=None, **kwargs) -> StationList:
    """
          Get stations which match the genre specified as query.
          :param genre_id: genre id
          :param br: bitrate
          :param k: API Dev Key.
          :param limit: limit the number of stations to return by passing the limit parameter. for example
          `limit=(X,Y)` - Y is the number of results to return and X is the offset.
          :param kwargs:
              mt - Filter the stations based on media type specified, MP3 = audio/mpeg and AAC+ = audio/aacp
          :return: `List[Stations]`
       """

    if not br and not genre_id:
        raise Exception('genre_id or br is required')

    endpoint = "/station/advancedsearch?k={}&f=json".format(k)
    endpoint += _build_url(limit, br=br, genre_id=genre_id, **kwargs)

    return _handle_url_action_json(endpoint, session=session)


def get_random_station(k, limit: (int, Tuple) = None, session=None, **kwargs):
    """
          Get random stations on SHOUTcast Radio Directory. Random stations can be restricted
          to the Bitrate/Genre/Media type specified.
          :param k: API Dev Key.
          :param limit: limit the number of stations to return by passing the limit parameter. for example
          `limit=(X,Y)` - Y is the number of results to return and X is the offset.
          :param kwargs:
              br - Filter the stations based on bitrate specified.
              mt - Filter the stations based on media type specified, MP3 = audio/mpeg and AAC+ = audio/aacp
              genre - Genre to filter the station result.
          :return: `List[Stations]`
       """

    endpoint = "/station/randomstations?k={}&f=json".format(k)
    endpoint += _build_url(limit, **kwargs)

    return _handle_url_action_json(endpoint, session=session)
