# staroid-python
Staroid python client library

## Install

```bash
pip install staroid
```

## Quickstart


Initialize

```python
from staroid import Staroid

# with no argument, it searches configuration ~/.staroid/config first and then try in-cluster configuration
strd = Staroid()

# alternatively, pass access token through the argument
strd = Staroid(access_token="<access token>", org="<org_name>")
```

Select cluster

```python
cluster1 = strd.cluster("<cluster_name>")
```