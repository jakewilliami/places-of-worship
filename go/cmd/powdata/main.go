package main

// NOTE: Reason for using Go: reflection
//   - https://go.dev/ref/spec#Struct_types
//   - https://go.dev/ref/spec#Tag
//   - https://go.dev/wiki/Well-known-struct-tags
//   - https://stackoverflow.com/q/10858787

// NOTE: based on Nick's stuff, it looks like they only use Google Maps to get date information.  This is of course very important to us

// TODO: https://overturemaps.org/
// TODO: Google Maps
// TODO: Charities Register (NZ)
// TODO: DBPedia
// TODO: https://www.openhistoricalmap.org/
// TODO: Census - https://www.stats.govt.nz/2023-census/
// TODO: Overture - https://uoa-eresearch.github.io/overture_nz/overture_NZ.csv; https://raw.githubusercontent.com/OvertureMaps/schema/main/task-force-docs/places/overture_categories.csv

// TODO: historic: church; shop: religion; building: religious; building: cathedral; building: chapel; building: church; building: monestery; building: mosque; building: presbytery; building: shrine; building: synagogue; building: temple
// Similar to https://github.com/UoA-eResearch/religion/blob/1a4c2495/download.sh

// TODO: make sure to tag the meta-data from source (watts2022building); e.g., these data are from google and these are from osm

// TODO: if we are to combine this with another database, how do we do that?  What is the combing factor?

import (
	"github.com/jakewilliami/places-of-worship/internal/dbpedia"
	"github.com/jakewilliami/places-of-worship/internal/osm"
)

func main() {
	osm.GetChurchData()
	dbpedia.GetChurchData()
}
