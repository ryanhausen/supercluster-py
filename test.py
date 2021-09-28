# this is a python port of supercluster.js
# https://github.com/mapbox/supercluster
#
# released under the following license ISC License
#
# Copyright (c) 2021, Mapbox
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
import json

from numpy import load
from supercluster import Supercluster

with open("places.json", "r") as f:
    PLACES = json.load(f)
with open("places-z0-0-0.json", "r") as f:
    PLACES_TILE = json.load(f)
with open("places-z0-0-0-min5.json", "r") as f:
    PLACES_TILE_MIN_5 = json.load(f)


def test_generates_clusters_properly():
    index = Supercluster().load(PLACES["features"])
    tile = index.get_tile(0, 0, 0)
    assert tile["features"] == PLACES_TILE["features"]


def test_supports_min_points_option():
    index = Supercluster(min_points=5).load(PLACES["features"])
    tile = index.get_tile(0, 0, 0)
    assert tile["features"] == PLACES_TILE_MIN_5["features"]


def test_returns_cluster_children():
    index = Supercluster().load(PLACES["features"])
    childCounts = index.get_children(164)
    childCounts = list(map(
        lambda p: p["properties"].get("point_count", 1),
        childCounts
    ))
    expected_childcounts = [6, 7, 2, 1]
    assert childCounts==expected_childcounts



def test_returns_cluster_leaves():
    index = Supercluster().load(PLACES["features"])
    leaf_names = list(map(lambda p: p["properties"]["name"], index.get_leaves(164, 10, 5)))
    expected_names = [
        "Niagara Falls",
        "Cape San Blas",
        "Cape Sable",
        "Cape Canaveral",
        "San  Salvador",
        "Cabo Gracias a Dios",
        "I. de Cozumel",
        "Grand Cayman",
        "Miquelon",
        "Cape Bauld",
    ]

    assert leaf_names == expected_names

def test_generates_unique_ids():
    index = Supercluster(generate_id=True).load(PLACES["features"])
    tile_vals = index.get_tile(0, 0, 0)["features"]
    ids = list(
        map(
            lambda f: f["id"],
            filter(
                lambda f: not f["tags"].get("cluster", False),
                tile_vals
            )
        )
    )
    expected_ids =  [12, 20, 21, 22, 24, 28, 30, 62, 81, 118, 119, 125, 81, 118]
    assert ids == expected_ids


def test_get_leaves_handles_null_props_features():
    index = Supercluster().load(PLACES["features"] + [dict(
        type="Feature",
        properties=None,
        geometry=dict(
            type="Point",
            coordinates=[-79.04411780507252, 43.08771393436908]
        ),
    )])

    leaves = index.get_leaves(165, 1, 6)
    assert leaves[0]["properties"] is None


def test_returns_cluster_expansion_zoom():
    index = Supercluster().load(PLACES["features"])
    assert index.get_cluster_expansion_zoom(164)==1
    assert index.get_cluster_expansion_zoom(196)==1
    assert index.get_cluster_expansion_zoom(516)==2
    assert index.get_cluster_expansion_zoom(996)==2
    assert index.get_cluster_expansion_zoom(2020)==3


def test_cluster_expansion_zoom_for_max_zoom():
    index = Supercluster(radius=60, extent=256, max_zoom=4).load(PLACES["features"])
    assert index.get_cluster_expansion_zoom(2599)==5


def test_aggregates_cluster_properties_with_reduce():
    def reduce_f(a, b):
        a["sum"] = a.get("sum", 0) + b["sum"]
        return a

    index = Supercluster(
        map=lambda props: dict(sum=props["scalerank"]),
        reduce=reduce_f,
        radius=100
    ).load(PLACES["features"])

    expected_values = [146, 84, 63, 23, 34, 12, 19, 29, 8, 8, 80, 35]
    actual_values = list(map(
        lambda f: f["tags"]["sum"],
        filter(
            lambda f: "sum" in f["tags"],
            index.get_tile(1, 0, 0)["features"]
        )
    ))
    assert expected_values == actual_values

    expected_values = [298, 122, 12, 36, 98, 7, 24, 8, 125, 98, 125, 12, 36, 8]
    actual_values = list(map(
        lambda f: f["tags"]["sum"],
        filter(
            lambda f: "sum" in f["tags"],
            index.get_tile(0, 0, 0)["features"]
        )
    ))
    assert expected_values == actual_values


def test_returns_clusters_when_query_crosses_international_dateline():
    index = Supercluster().load([
        {
            "type": "Feature",
            "properties": None,
            "geometry": {
                "type": "Point",
                "coordinates": [-178.989, 0]
            }
        }, {
            "type": "Feature",
            "properties": None,
            "geometry": {
                "type": "Point",
                "coordinates": [-178.990, 0]
            }
        }, {
            "type": "Feature",
            "properties": None,
            "geometry": {
                "type": "Point",
                "coordinates": [-178.991, 0]
            }
        }, {
            "type": "Feature",
            "properties": None,
            "geometry": {
                "type": "Point",
                "coordinates": [-178.992, 0]
            }
        }
    ])


    nonCrossing = index.get_clusters([-179, -10, -177, 10], 1)
    crossing = index.get_clusters([179, -10, -177, 10], 1)

    assert len(nonCrossing)
    assert len(crossing)
    assert len(nonCrossing) == len(crossing)


def test_does_not_crash_on_weird_bbox_values():
    index = Supercluster().load(PLACES["features"])
    assert len(index.get_clusters([129.426390, -103.720017, -445.930843, 114.518236], 1)) == 26
    assert len(index.get_clusters([112.207836, -84.578666, -463.149397, 120.169159], 1)) == 27
    assert len(index.get_clusters([129.886277, -82.332680, -445.470956, 120.390930], 1)) == 26
    assert len(index.get_clusters([458.220043, -84.239039, -117.137190, 120.206585], 1)) == 25
    assert len(index.get_clusters([456.713058, -80.354196, -118.644175, 120.539148], 1)) == 25
    assert len(index.get_clusters([453.105328, -75.857422, -122.251904, 120.732760], 1)) == 25
    assert len(index.get_clusters([-180, -90, 180, 90], 1)) == 61


def test_same_location_points_are_clustered():
    index = Supercluster(
        max_zoom=20,
        extent=8192,
        radius=16
    ).load([
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-1.426798, 53.943034]}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-1.426798, 53.943034]}},
    ])

    assert len(index.trees[20].ids)==1


def test_ensure_unclustered_point_coords_are_not_rounded():
    index = Supercluster(max_zoom=19).load([
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [173.19150559062456, -41.340357424709275]}}
    ])

    assert index.get_tile(20, 1028744, 656754)["features"][0]["geometry"][0] == [421, 281]


if __name__=="__main__":
    # test_generates_clusters_properly()
    # test_supports_min_points_option()
    # test_returns_cluster_children()
    # test_returns_cluster_leaves()
    # test_generates_unique_ids()
    test_ensure_unclustered_point_coords_are_not_rounded()