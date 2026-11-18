USERS = {
    1: {
        "first_name": "Doãn",
        "last_name": "Lợi",
        "email": "Doan.Loi@example.com",
    },
    2: {
        "first_name": "An",
        "last_name": "Trần",
        "email": "an.tran@example.com",
    },
    42: {
        "first_name": "Nem",
        "last_name": "Chua",
        "email": "nem.chua@example.com",
    },
}


def get_user(uid: int):
    return USERS.get(uid)
