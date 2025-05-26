package osm

import (
	"bytes"
	"context"
	"errors"
	// "encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	// "net/url"
	// "encoding/xml"
	// "strings"

	jsoniter "github.com/json-iterator/go"
	"github.com/paulmach/osm"
	// "github.com/paulmach/orb/geojson"
	"github.com/paulmach/osm/osmapi"
	// "github.com/paulmach/osm/osmgeojson"
)

func GetChurchData() {
	// Overpass QL query to get churches in New Zealand
	// https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dplace_of_worship

	// nz_bounds = box(163.08,-50.12,180,-31.31)
	overpassQL := `
        [out:json][timeout:999];
        area["ISO3166-1"="NZ"][admin_level=2]->.nz;
        (
            // node["amenity"="place_of_worship"]["religion"="christian"](area.nz);
            node["amenity"="place_of_worship"](area.nz);
            // way["amenity"="place_of_worship"]["religion"="christian"](area.nz);
            way["amenity"="place_of_worship"](area.nz);
            // relation["amenity"="place_of_worship"]["religion"="christian"](area.nz);
            relation["amenity"="place_of_worship"](area.nz);
        );
        out body;
        >;
        out skel qt;
    `

	// Send the POST request to Overpass API
	log.Println("Pulling data from Overpass API...")
	resp, err := http.Post(
		"https://overpass-api.de/api/interpreter",
		"application/x-www-form-urlencoded",
		bytes.NewBufferString("data="+overpassQL),
	)
	if err != nil {
		log.Fatalf("failed to query Overpass API: %v", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		// TODO: defer
		log.Fatalf("failed to read response body: %v", err)
	}

	log.Printf("Retrieved %s from Overpass API", humanReadableBytes(len(data)))

	o := &osm.OSM{}
	err = jsoniter.Unmarshal(data, &o)
	if err != nil {
		log.Fatalf("unmarshal error: %v", err)
	}

	log.Printf("Found %d nodes/records", len(o.Nodes))

	if len(o.Ways) > 0 {
		log.Printf("Warning: Ways are not currently handled, yet %d were found", len(o.Ways))
	}

	if len(o.Relations) > 0 {
		log.Printf("Warning: Relations are not currently handled, yet %d were found", len(o.Relations))
	}

	log.Printf("%#v", o.Nodes[0])

	religions := make(map[string]int)
	for i := 0; i < len(o.Nodes); i++ {
		node := o.Nodes[i]
		print := false

		for _, religion := range nodeReligions(node) {
			religions[religion]++
			if religion == "maori" {
				print = true
			}
		}

		// Print if we are interested
		if print || true {
			name, err := getNodeName(node)

			// Set name if not known
			if err != nil {
				name = "Unknown"
			}

			if print || name != "Ancient Maori wall" {
				continue
			}

			// log.Printf("%#v", node)
			log.Printf("[%d: %s] %f, %f", node.ID, name, node.Lat, node.Lon)
			ctx := context.Background()
			history, err := osmapi.NodeHistory(ctx, node.ID)

			if err != nil {
				log.Fatalf("cannot get history for node ID %d: %v", node.ID, err)
			}

			for j := 0; j < len(history); j++ {
				histNode := history[j]
				changeset, err := osmapi.Changeset(ctx, histNode.ChangesetID)
				if err != nil {
					log.Fatalf("failed to get details of changeset for node %d@%d: %v", node.ID, histNode.ChangesetID, err)
				}
				log.Printf("    %#v", changeset)
			}
		}
	}

	log.Printf("%#v", religions)

	// Find changeset of interest
	log.Printf("%d", len(o.Changesets))
	for i := 0; i < len(o.Changesets); i++ {
		c := o.Changesets[i]
		if c.ID != 0 {
			log.Printf("%#v", c)
			break
		}
	}

	// ctx := context.Background()
	// osmapi.NodeHistory()

	// log.Printf("%#v", religions)

	// var c = jsoniter.Config{
	// EscapeHTML:              true,
	// SortMapKeys:             false,
	// MarshalFloatWith6Digits: true,
	// }.Froze()

	// osm.CustomJSONMarshaler = c
	// osm.CustomJSONUnmarshaler = c

	/*delta := 0.0001

	lon, lat := 175.2793, -37.7870;
	bounds := &osm.Bounds{
		MinLat: lat - delta, MaxLat: lat + delta,
		MinLon: lon - delta, MaxLon: lon + delta,
	}

	ctx := context.Background()
	o, _ := osmapi.Map(ctx, bounds) // fetch data from the osm api.

	// run the conversion
	fc, err := osmgeojson.Convert(o)

	// marshal the json
	gj, _ := json.MarshalIndent(fc, "", " ")
	fmt.Println(string(gj))*/

	// log.Printf("Retrieved %d bytes from Overpass API", len(bodyBytes))
	// log.Info("")

	// Read and decode the OSM XML response

	/*
		scanner := osm.New(context.Background(), f, 3)

		data, err := io.ReadAll(resp.Body)
		if err != nil {
			log.Fatalf("failed to read response body: %v", err)
		}

		decoder := osm.NewDecoder(bytes.NewReader(data))
		err = decoder.Decode()
		if err != nil {
			log.Fatalf("failed to decode OSM XML: %v", err)
		}

		osmData := decoder.Data()

		// Example: Print church nodes with name if available
		for _, node := range osmData.Nodes {
			name := node.Tags.Find("name")
			fmt.Printf("Church Node ID: %d, Name: %s, Lat: %.5f, Lon: %.5f\n",
				node.ID, name, node.Lat, node.Lon)
		}
	*/
}

func humanReadableBytes(bytes int) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%d B", bytes)
	}
	div, exp := float64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.2f %cB", float64(bytes)/div, "KMGTPE"[exp])
}

func getNodeName(node *osm.Node) (string, error) {
	for i := 0; i < len(node.Tags); i++ {
		tag := node.Tags[i]

		// Set name
		if tag.Key == "name" {
			name := tag.Value
			return name, nil
		}
	}

	return "", errors.New("name tag not found for node")
}

func nodeReligions(node *osm.Node) []string {
	// TODO: handle different queries

	var religions []string

	for i := 0; i < len(node.Tags); i++ {
		tag := node.Tags[i]

		if tag.Key == "religion" {
			religion := tag.Value
			religions = append(religions, religion)
		}
	}

	return religions
}

func nodeIsPlaceOfWorship(node *osm.Node) bool {
	religions := nodeReligions(node)
	return len(religions) > 0
}

func findkjsdfkjdn(node *osm.Node) string {
	ctx := context.Background()
	hist, err := osmapi.NodeHistory(ctx, node.ID)
	if err != nil {
		log.Fatalf("cannot get history for node ID %d: %v", node.ID, err)
	} else {
		for j := 0; j < len(hist); j++ {
			log.Printf("%#v", hist[0])
		}
	}
	return ""
}
