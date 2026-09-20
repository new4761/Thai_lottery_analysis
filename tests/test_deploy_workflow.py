from pathlib import Path
import unittest


WORKFLOW = Path(".github/workflows/deploy.yml").read_text()


class DeployWorkflowTests(unittest.TestCase):
    def test_commit_comment_uses_supported_github_request(self):
        self.assertIn("uses: actions/github-script@v9", WORKFLOW)
        self.assertIn(
            "github.request('POST /repos/{owner}/{repo}/commits/{commit_sha}/comments'",
            WORKFLOW,
        )

    def test_commit_comment_remains_push_only(self):
        self.assertIn("if: github.event_name == 'push'", WORKFLOW)

    def test_pages_deployment_is_unchanged(self):
        self.assertIn("uses: peaceiris/actions-gh-pages@v3", WORKFLOW)
        self.assertIn("destination_dir: tools/lottery/generator", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
