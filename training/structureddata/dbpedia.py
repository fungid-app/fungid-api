from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql/")

sparql.setReturnFormat(JSON)

sparql.setQuery("""
SELECT ?property ?hasValue ?isValueOf
WHERE {
  { <http://dbpedia.org/resource/Template:Mycomorphbox> ?property ?hasValue }
  UNION
  { ?isValueOf ?property <http://dbpedia.org/resource/Template:Mycomorphbox> }
}"""
                )


try:
    ret = sparql.queryAndConvert()

    for r in ret["results"]["bindings"]:
        print(r)
except Exception as e:
    print(e)
