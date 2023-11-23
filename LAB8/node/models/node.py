class RESTNode:

    def __init__(self, leader, followers = None):
        self.leader = leader

        if self.leader:
            self.followers = followers

    def to_string(self):
        print(f"Is leader: {self.leader}")
        if self.leader:
            print(f"Followers: {self.followers}")
