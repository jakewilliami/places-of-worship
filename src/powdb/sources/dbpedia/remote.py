from enum import StrEnum
from urllib.parse import urlencode

import requests


def get_church_data():
    # https://dbpedia.org/ontology/placeOfWorship
    # TODO: https://sparqlwrapper.readthedocs.io/en/latest/main.html
    query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?building ?label ?country ?location ?locationCountry ?address
        WHERE {
          ?building a dbo:ReligiousBuilding .
          OPTIONAL { ?building rdfs:label ?label }
          OPTIONAL { ?building dbo:country ?country }
          OPTIONAL {
            ?building dbo:location ?location .
            OPTIONAL { ?location dbo:country ?locationCountry }
          }
          OPTIONAL { ?building dbo:address ?address }
        }
        # LIMIT 1
    """

    results = query_dbpedia(query)
    print(f"Received {len(str(results))} bytes from DBpedia")
    print(results)
    return results


class MIMEType(StrEnum):
    HTML = "text/html"
    JSON = "application/json"


def build_dbpedia_query(query: str, out_type: MIMEType) -> str:
    trimmed_query = "\n".join(line.strip() for line in query.splitlines())
    base_uri = "https://dbpedia.org/sparql"
    params = {
        "default-graph-uri": "http://dbpedia.org",
        # "query": strings.ReplaceAll(query, "\n", " "),
        "query": trimmed_query,
        "format": str(out_type),
        "timeout": "30000",
        "signal_void": "on",
        "signal_unconnected": "on",
    }

    return f"{base_uri}?{urlencode(params, doseq=True)}"


def query_dbpedia(query: str) -> str:
    # TODO: MIMETextHTML is not yet supported
    uri = build_dbpedia_query(query, MIMEType.JSON)
    resp = requests.get(uri)
    resp.raise_for_status()
    return resp.json()


# NOTE: sometimes we know roughtly the area but not specifically
