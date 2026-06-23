def topic(id: int) -> dict[int, list[str]]:

    with open(str(id) + "_td.txt", "r", encoding="utf-8") as f:

        lignes = f.readlines()


    sec ={"section":id}

    return sec
