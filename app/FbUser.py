import facebook


class FbUser:
    def __init__(self, token):
        self.token = token
        self.graph = None
        self.profPic = None
        self.id = None
        self.name = None

    def initialize(self):
        self.graph = facebook.GraphAPI(access_token=self.token)

        tmp = self.graph.get_object(id='me', fields='name,picture{url}')

        self.id = tmp['id']
        self.name = tmp['name']
        self.profPic = tmp['picture']['data']['url']

