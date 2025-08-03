from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass


def nz():
    nominatim = Nominatim()
    return nominatim.query("NZ")


def get_church_data():
    overpass = Overpass()
    # query = overpassQueryBuilder(area=nz(), elementType="node", )
    query = """
        // [out:json][timeout:999];
        area["ISO3166-1"="NZ"][admin_level=2]->.nz;
        (
            // node["amenity"="place_of_worship"]["religion"="christian"]
            //   (area.nz);
            node["amenity"="place_of_worship"](area.nz);
            // way["amenity"="place_of_worship"]["religion"="christian"]
            //   (area.nz);
            way["amenity"="place_of_worship"](area.nz);
            // relation["amenity"="place_of_worship"]["religion"="christian"]
            //   (area.nz);
            relation["amenity"="place_of_worship"](area.nz);
        );
        out body;
        >;
        out skel qt;
    """
    result = overpass.query(query, timeout=999, out="json")

    if result.isValid():
        data = result.toJSON()
    else:
        print("ERROR: invalid response from Overpass")
        return

    print(f"Received {len(str(data))} bytes from OSM (Overpass)")


# TODO: collapse ways function

# def overpassQueryBuilder(
#         area=None,
#         bbox=None,
#         polygon=None,
#         elementType=None,
#         selector=[],
#         conditions=[],
#         since=None,
#         to=None,
#         userid=None,
#         user=None,
#         includeGeometry=False,
#         includeCenter=False,
#         out='body'
# ):
