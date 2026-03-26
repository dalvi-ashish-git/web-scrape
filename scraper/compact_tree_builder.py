def build_compact_tree(extracted_data):
    """
    Builds minimal tree from extracted content
    """

    tree = []

    for item in extracted_data:
        node = {
            "tag": item["tag"],
            "text": item["text"],
            "attrs": item.get("attrs", {})
        }
        tree.append(node)

    return tree