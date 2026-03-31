from datetime import datetime, timedelta

from requests.auth import HTTPBasicAuth
from fastapi import HTTPException
from http import HTTPStatus
from config import settings
from services.http_client import request_json

from logzero import logger
#import connection
import secrets_sf
import requests
import os


class RAApiError(Exception):
    pass

class RAApiAuthError(RAApiError):
    pass

class RAApiTimeoutError(RAApiError):
    pass

class RAApiRequestError(RAApiError):
    pass

class RAApiConnectionError(RAApiError):
    pass

class RAApiMalformedServiceResponse(RAApiError):
    pass

#_________________________________________________________________________________
def _auth() -> HTTPBasicAuth | None:
    if settings.ra_api_username and settings.ra_api_password:
        return HTTPBasicAuth(settings.ra_api_username, settings.ra_api_password)
    return None

#_________________________________________________________________________________
async def delete_reservation(pgroup: str, partition: str, nodes: int, days: int) -> dict:
    pass

#_________________________________________________________________________________
async def create_reservation(pgroup: str, partition: str, nodes: int, days: int) -> dict:
    url = f'{settings.ra_api_base_url}/reservations'
    payload = {
        'pgroup': pgroup,
        'partition': partition,
        'nodes': nodes,
        'days': days,
    }

    try:
        data = request_json(
            'POST',
            url,
            auth=_auth(),
            json=payload,
        )
        if not isinstance(data, dict):
            raise RAApiRequestError('Unexpected response from backend')
        return data
    except Exception:
        start = datetime.now()
        end = start + timedelta(days=days)
        return {
            'reservation_name': f'{pgroup}_{partition}',
            'pgroup': pgroup,
            'partition': partition,
            'nodes': nodes,
            'start': start.strftime('%Y-%m-%d %H:%M'),
            'end': end.strftime('%Y-%m-%d %H:%M'),
            'status': 'created (stub)',
        }

#_________________________________________________________________________________
def fetch_cluster_status() -> list[dict]:
    url = settings.ra_api_base_url
    logger.debug(f"[GET] Contacting url {url}")
    headers = { "Content-Type": "application/json", "apikey": f"{secrets_sf.tokens['ra_api_admin_token']}" }
    #code, json_result = connection.get( url, data, None )

    try:   
        response = requests.get(url, headers=headers, json=None, verify=False,timeout=(5, 30))
    except requests.exceptions.ConnectionError as err:
        message = f"Connection error: {err}"
        logger.error( message )
        raise RAApiConnectionError( message )
    except requests.exceptions.RequestException as err:
        message = f"Connection error: {err}"
        logger.error( message )
        raise RAApiRequestError( message )
    except Exception as err:
        message = f"Unexpected error: {err}"
        logger.error( message )  # log con stack trace
        raise RAApiError( message )
    
    logger.debug(f"[GET] Service Response=[{response}]")

    if response.status_code == 200:

        response_json = None
        try: 
            response_json = response.json()
            logger.debug(f"[GET] Json Service Response=[{response_json}]")
        except Exception as err:
            message = f"Error deserializing the response string into a json object: {err}"
            logger.error( message )
            raise RAApiError( message )

        if 'data' not in response_json:
            message = "Malformed response from Service: 'data' is missing the json response"
            logger.error( message )
            raise RAApiMalformedServiceResponse( message )

        data = response_json['data']

        partitions = []
        for item, subjson in data.items():
            this_partition  = {}
            this_partition['name']             = item
            this_partition['totcores']         = subjson['cores']
            this_partition['totnodes']         = subjson['nodes']
            this_partition['totgpus']          = subjson['gpus']
            this_partition['res']              = subjson['resources']
            this_partition['state']            = subjson['state']
            this_partition['max_job_duration'] = subjson['max_job_time']
            this_partition['configured_nodes'] = subjson['configured_nodes']
            partitions.append(this_partition)

        return partitions
    
    else:
        raise RAApiError (
             HTTPException(
                status_code=response.status_code,
                detail = {
                    'message': f"HTTP code {response.status_code}. {HTTPStatus(response.status_code).name}: {HTTPStatus(response.status_code).description}",
                    'errors': f"HTTP code {response.status_code}. {HTTPStatus(response.status_code).name}: {HTTPStatus(response.status_code).description}"
                }
            )
        )
    
#_________________________________________________________________________________
def fetch_reservation_details(reservation_name: str) -> dict:
    """Stub iniziale; poi qui metterai la vera REST call."""
    fake_data = {
        'res-admin-001': {
            'name': 'res-admin-001',
            'owner': 'dorigo_a',
            'partition': 'admin',
            'start_time': '2026-03-31 08:00',
            'end_time': '2026-03-31 18:00',
            'state': 'ACTIVE',
            'nodes': 'ra-c-[051-053]',
        },
        'res-gpu-002': {
            'name': 'res-gpu-002',
            'owner': 'dorigo_a',
            'partition': 'gpu',
            'start_time': '2026-03-31 09:00',
            'end_time': '2026-03-31 12:00',
            'state': 'PLANNED',
            'nodes': 'ra-gpu-[001-002]',
        },
        'res-weekend-003': {
            'name': 'res-weekend-003',
            'owner': 'guest01',
            'partition': 'week',
            'start_time': '2026-04-04 00:00',
            'end_time': '2026-04-05 23:59',
            'state': 'PLANNED',
            'nodes': 'ra-c-[101-110]',
        },
    }

    return fake_data.get(reservation_name, {})