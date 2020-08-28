# staroid-python
Staroid python client library

## Install

```bash
pip install staroid
```

## Quickstart


```python
from staroid import Staroid

star = Staroid()

# Create a ske kubernetes cluster
my_cluster = star.cluster().create("my cluster", "gcp us-west1")

# Launch a project 
ns = star.namespace(my_cluster).create("my_app", "GITHUB/staroids/namespace:master")

# stop instance
ns = star.namespace(my_cluster).stop("my_app")

# restart instance
ns = star.namespace(my_cluster).start("my_app")

# delete instance
ns = star.namespace(my_cluster).delete("my_app")
```

## Configuration

### Environment variables

| Env variable | optional | description |
| ------------- | ---------- | ------------ |
| STAROID_ACCESS_TOKEN | false | Access token generated from [here](https://staroid.com/settings/accesstokens) |
| STAROID_ACCOUNT | true | Account to use. e.g. `GITHUB/my_github_login` |

### Config file

Altanatively, you can create `~/.staroid/config.yaml` file like below.

```yaml
access_token: <your access token> # access token from https://staroid.com/settings/accesstokens
account: <account> # optional. e.g. "GITHUB/my_github_login"
```

When both config file and environment variables exist, environment variable will take precedence.
