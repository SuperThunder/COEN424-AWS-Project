
GEO_RADIUS_LIMIT_METRE = '25000' # radius for search cannot be larger than 4000 metres. has to be a string for lambda environment.
OPENSEARCH_WIFI_NETWORK_INDEX = 'wifinetworks'
OPENSEARCH_GET_WIFI_NETWORK_LIMIT = '100'  # no more than 100 results per search

# POPULATE AFTER CREATING THE OPENSEARCH DOMAIN
OPENSEARCH_URL = 'search-opensearchdomai-o7gwawokyt2v-bwi3zrhw3hq6z7repaogfmk6eu.us-east-2.es.amazonaws.com'
OPENSEARCH_MASTER_USER_SECRET_ARN = 'arn:aws:secretsmanager:us-east-2:391508643370:secret:OpenSearchDomain424ProjectM-S6QcgooliSeK-xsxYQe'

# POPULATE AFTER FRONTEND / AUTH SETUP
USER_POOL_ARN = 'arn:aws:cognito-idp:us-east-1:391508643370:userpool/us-east-1_kAwDmW6mJ'
USER_POOL_ID = 'us-east-1_kAwDmW6mJ'