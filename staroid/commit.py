class Commit:
    def __init__(self, commit_url):
        self.__commit_url = commit_url

        commit_hash_pos = commit_url.find("#")
        if commit_hash_pos > 0:
            self.__commit = commit_url[commit_hash_pos + 1:]
        else:
            self.__commit = ""
        
        branch_pos = commit_url.find(":")
        if branch_pos < 0:
            raise Exception("Branch is missing")

        if commit_hash_pos > 0:
            self.__branch = commit_url[branch_pos + 1:commit_hash_pos]
        else:
            self.__branch = commit_url[branch_pos + 1:]

        if len(self.__branch) == 0:
            raise Exception("Branch is missing")
            
        proj = commit_url[:branch_pos].split("/")
        if len(proj) != 3:
            raise Exception("Invalid project format")

        self.__provider = proj[0]
        self.__owner = proj[1]
        self.__repo = proj[2]

    def url(self):
        return self.__commit_url

    def provider(self):
        return self.__provider

    def owner(self):
        return self.__owner

    def repo(self):
        return self.__repo
    
    def branch(self):
        return self.__branch

    def commit(self):
        return self.__commit
