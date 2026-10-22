#!/bin/bash
# Create private repo argo-fetch, push workflow + scraper, dispatch.
set -e
TOKEN=$(cat /home/z/my-project/.gh_token)
API=https://api.github.com
OWNER=limitlessprojects
REPO=argo-fetch
AUTH="Authorization: Bearer $TOKEN"
CT="Content-Type: application/json"

echo "== 1. create repo (private, auto_init) =="
curl -sS -X POST -H "$AUTH" -H "$CT" "$API/user/repos" -d '{
  "name":"argo-fetch","private":true,"auto_init":true,
  "description":"throwaway egress probe: fetch a claude artifact from Actions runners"
}' | python3 -c "import json,sys;d=json.load(sys.stdin);print('created:',d.get('full_name') or d.get('message'))"

echo "== 2. push scrape.py =="
B64=$(base64 -w0 /home/z/my-project/scripts/argon-fetch/scrape.py)
curl -sS -X PUT -H "$AUTH" -H "$CT" \
  "$API/repos/$OWNER/$REPO/contents/scrape.py" \
  -d "{\"message\":\"scraper\",\"content\":\"$B64\",\"branch\":\"main\"}" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print('scrape.py:',d.get('commit',{}).get('sha','?')[:8] if 'commit' in d else d.get('message'))"

echo "== 3. push fetch.yml =="
B64=$(base64 -w0 /home/z/my-project/scripts/argon-fetch/fetch.yml)
curl -sS -X PUT -H "$AUTH" -H "$CT" \
  "$API/repos/$OWNER/$REPO/contents/.github/workflows/fetch.yml" \
  -d "{\"message\":\"workflow\",\"content\":\"$B64\",\"branch\":\"main\"}" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print('fetch.yml:',d.get('commit',{}).get('sha','?')[:8] if 'commit' in d else d.get('message'))"

sleep 3
echo "== 4. dispatch =="
CODE=$(curl -sS -o /tmp/disp.out -w "%{http_code}" -X POST -H "$AUTH" -H "$CT" \
  "$API/repos/$OWNER/$REPO/actions/workflows/fetch.yml/dispatches" -d '{"ref":"main"}')
echo "dispatch http=$CODE $(cat /tmp/disp.out | head -c 200)"
