SUBDOMAIN=$1
DOMAIN=$2

node hash_finder.js "${SUBDOMAIN}" ${DOMAIN} ./hars/${SUBDOMAIN}${DOMAIN}.har ./general_news_cnames/${SUBDOMAIN}${DOMAIN}_cname_out.json
#node hash_finder.js "" ./hars/elpais.com.har ./general_news_cnames/elpais.com_cname_out.json
