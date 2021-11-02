
GEO_RADIUS_LIMIT_METRE = '2000m' # radius for search cannot be larger than 2000 metres. has to be a string for lambda environment.
OPENSEARCH_WIFI_NETWORK_INDEX = 'wifinetworks'
OPENSEARCH_GET_WIFI_NETWORK_LIMIT = '100' # no more than 100 results per search

# POPULATE AFTER CREATING THE OPENSEARCH DOMAIN
OPENSEARCH_MASTER_USER_SECRET_ARN = 'arn:aws:secretsmanager:us-east-2:391508643370:secret:OpenSearchDomain424ProjectM-9Q1z5ZTlBvMA-0CNVsx'