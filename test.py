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
from supercluster import Supercluster

with open("places.json", "r") as f:
    PLACES = json.load(f)
with open("places-z0-0-0.json", "r") as f:
    PLACES_TILE = json.load(f)
with open("places-z0-0-0-min5.json", "r") as f:
    PLACES_TILE_MIN_5 = json.load(f)

def test_generates_clusters_properly():
    index = Supercluster(extent=512).load(PLACES["features"])
    tile = index.get_tile(0, 0, 0)
    assert tile["features"] == PLACES_TILE["features"]


if __name__=="__main__":
    test_generates_clusters_properly()