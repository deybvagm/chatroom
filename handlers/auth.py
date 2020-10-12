users = {
    'nick': 'MTIz',
    'user1': 'MTIz',
    'user2': 'MTIz',
    'user3': 'MTIz'
}


def validate_authentication(username, unchecked_pass):
    passw = users.get(username)
    return True if passw is not None and passw == unchecked_pass else False





