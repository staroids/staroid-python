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

# create a ske kubernetes cluster
my_cluster = star.cluster().create("my cluster", "gcp us-west1")

# create a namespace and deploy project 
ns = star.namespace(my_cluster).create("my_app", "GITHUB/staroids/namespace:master")
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
