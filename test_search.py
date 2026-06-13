from search_qdrant import retrieve_pages

results = retrieve_pages(
    "what is the color of pie chart"
)

for point in results:

    print(
        point.payload["page_path"]
    )

    print(
        point.score
    )

    print()