def runnable(nodes):
    return [
        node
        for node in nodes.values()
        if node.status == "pending"
        and all(
            nodes[d].status == "completed"
            for d in node.depends_on
        )
    ]
