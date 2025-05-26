package dbpedia

import (
	// "bytes"
	// "context"
	// "errors"
	// "encoding/json"
	// "fmt"
	// "io"
	"log"
	// "net/http"
	"net/url"
	// "encoding/xml"
	// "strings"
	// jsoniter "github.com/json-iterator/go"
	// "github.com/paulmach/osm"
	// "github.com/paulmach/orb/geojson"
	// "github.com/paulmach/osm/osmapi"
	// "github.com/paulmach/osm/osmgeojson"
)

func GetChurchData() {
	// TODO: Dbpedia
	// https://stackoverflow.com/questions/48790879

	dbpediaQuery := `
        select distinct ?Concept 
        where {[] a ?Concept} LIMIT 100
    `
	results, err := queryDbpedia(dbpediaQuery)
	if err != nil {
		log.Fatalf("Could not query dbpedia's SPARQL: %v", err)
	}
	log.Printf("%#v", results)
	// query := `
	// https://dbpedia.org/sparql?default-graph-uri=http://dbpedia.org&query=select distinct ?Concept where {[] a ?Concept} LIMIT 100 &format=text/html&timeout=30000&signal_void=on&signal_unconnected=on
	// `

	// TODO: combine different source types like they do in json2parquet.json

	// http://api.live.dbpedia.org/sync/articles
}

func buildURI(base string, params map[string]string) (string, error) {
	u, err := url.Parse(base)
	if err != nil {
		return "", err
	}

	q := u.Query()
	for k, v := range params {
		q.Set(k, v)
	}
	u.RawQuery = q.Encode()
	return u.String(), nil
}

type MIMEType string

const (
	MIMETextHTML        MIMEType = "text/html"
	MIMEApplicationJSON MIMEType = "application/json"
)

func constructDbpediaQuery(query string, outType MIMEType) string {
	// This query path is scraped from https://dbpedia.org/sparql
	baseURI := "https://dbpedia.org/sparql"
	params := map[string]string{
		"default-graph-uri": "http://dbpedia.org",
		// "query": strings.ReplaceAll(query, "\n", " "),
		"query":              query,
		"format":             string(outType),
		"timeout":            "30000",
		"signal_void":        "on",
		"signal_unconnected": "on",
	}
	uri, err := buildURI(baseURI, params)
	if err != nil {
		log.Panicf("Could not build URI for query: %v", err)
	}
	return uri
	// fmt.Println(uri)
	// uri = `https://dbpedia.org/sparql?default-graph-uri=http://dbpedia.org&query=select distinct ?Concept where {[] a ?Concept} LIMIT 100 &format=text/html&timeout=30000&signal_void=on&signal_unconnected=on`

	// fmt.Sprintf("Content-Type: %s", mime)
}

/*type SparqlResponse struct {
	Head    Head     `json:"head"`
	Results Results  `json:"results"`
}

type Head struct {
	Vars []string `json:"vars"`
}

type Results struct {
	Bindings []Binding `json:"bindings"`
}

type Binding struct {
	Concept Value `json:"Concept"`
}*/

func queryDbpedia(query string) (string, error) {
	// TODO: MIMETextHTML is not yet supported, but to support it, will want to use github.com/nfx/go-htmltabl
	// uri := constructDbpediaQuery(dbpediaQuery, MIMEApplicationJSON)
	// https://dbpedia.org/ontology/placeOfWorship

	q := `PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?building WHERE {
  ?building a dbo:ReligiousBuilding .
}
LIMIT 10`
	return q, nil
}

// NOTE: sometimes we know roughtly the area but not specifically
// func queryCharities
