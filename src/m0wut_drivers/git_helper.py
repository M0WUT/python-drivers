from git import Repo
import pathlib


class GitHelper:
    def __init__(self, git_directory: pathlib.Path):
        self.dir = git_directory
        self.repo = Repo(self.dir)

    def get_git_version(self) -> str:
        head_commit = self.repo.head.commit
        last_commit_hash = head_commit.hexsha
        return f"{last_commit_hash} ({'Dirty' if self.repo.is_dirty() else 'Unmodified'})"
