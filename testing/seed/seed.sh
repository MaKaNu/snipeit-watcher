#!/bin/sh
# Seeds Snipe-IT through its REST API from /seed/manifest.json. Idempotent.
set -eu

API="${SNIPEIT_URL:-http://snipeit}/api/v1"
MANIFEST=/seed/manifest.json
TOKEN="$(cat /shared/token)"

apk add --no-cache curl jq >/dev/null

call() { # method path [json-body]
  curl -sS -X "$1" "$API$2" \
    -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" \
    ${3:+-d "$3"}
}

until [ "$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" -H 'Accept: application/json' "$API/statuslabels")" = 200 ]; do
  echo "waiting for Snipe-IT API..."; sleep 3
done

m() { jq -r "$1" "$MANIFEST"; }

find_id() { # path field value
  for extra in "" "&activated=false"; do
    [ -n "$extra" ] && [ "$1" != users ] && continue
    id="$(call GET "/$1?limit=500$extra" | jq -r --arg v "$3" --arg f "$2" '[.rows[]? | select(.[$f] == $v)][0].id // empty')"
    [ -n "$id" ] && break
  done
  echo "$id"
}

# Like call, but aborts when Snipe-IT answers with status != success (it replies HTTP 200 on errors).
call_ok() { # method path json-body
  resp="$(call "$1" "$2" "$3")"
  if [ "$(echo "$resp" | jq -r '.status // "error"')" != success ]; then
    echo "FAILED $1 $2: $resp" >&2
    exit 1
  fi
}

ensure() { # path field value body
  id="$(find_id "$1" "$2" "$3")"
  if [ -z "$id" ]; then
    resp="$(call POST "/$1" "$4")"
    id="$(echo "$resp" | jq -r '.payload.id // empty')"
    [ -n "$id" ] || { echo "failed to create $1 '$3': $resp" >&2; exit 1; }
    echo "created $1 '$3' (id $id)" >&2
  else
    echo "exists  $1 '$3' (id $id)" >&2
  fi
  echo "$id"
}

CAT_ID="$(ensure categories name "$(m .category)" "$(jq -n --arg n "$(m .category)" '{name:$n,category_type:"asset"}')")"
MAN_ID="$(ensure manufacturers name "$(m .manufacturer)" "$(jq -n --arg n "$(m .manufacturer)" '{name:$n}')")"
STA_ID="$(ensure statuslabels name "$(m .status_label)" "$(jq -n --arg n "$(m .status_label)" '{name:$n,type:"deployable"}')")"
MOD_ID="$(ensure models name "$(m .model)" "$(jq -n --arg n "$(m .model)" --argjson c "$CAT_ID" --argjson f "$MAN_ID" '{name:$n,category_id:$c,manufacturer_id:$f}')")"

PASS="$(m .default_password)"
: > /tmp/user_ids
user_id() { # username
  id="$(awk -v n="$1" '$1 == n {print $2}' /tmp/user_ids)"
  [ -n "$id" ] || { echo "FAILED: no id known for user '$1'" >&2; exit 1; }
  echo "$id"
}
# Users are created active so assets can be checked out; deactivation happens last.
jq -c '.users[]' "$MANIFEST" | while read -r u; do
  name="$(echo "$u" | jq -r .username)"
  body="$(echo "$u" | jq --arg p "$PASS" '.activated = true | .password = $p | .password_confirmation = $p')"
  echo "$name $(ensure users username "$name" "$body")" >> /tmp/user_ids
done

jq -c '.assets[]' "$MANIFEST" | while read -r a; do
  tag="$(echo "$a" | jq -r .asset_tag)"
  body="$(echo "$a" | jq --argjson s "$STA_ID" --argjson m "$MOD_ID" '{asset_tag,name,status_id:$s,model_id:$m}')"
  aid="$(ensure hardware asset_tag "$tag" "$body")"
  owner="$(echo "$a" | jq -r '.assigned_to // empty')"
  if [ -n "$owner" ]; then
    assigned="$(call GET "/hardware/$aid" | jq -r '.assigned_to.id // empty')"
    if [ -z "$assigned" ]; then
      uid="$(user_id "$owner")"
      call_ok POST "/hardware/$aid/checkout" "$(jq -n --argjson u "$uid" '{checkout_to_type:"user",assigned_user:$u}')"
      echo "checked out $tag to $owner"
    fi
  fi
done

jq -c '.users[] | select(.activated == false)' "$MANIFEST" | while read -r u; do
  name="$(echo "$u" | jq -r .username)"
  uid="$(user_id "$name")"
  call_ok PATCH "/users/$uid" '{"activated":false}'
  [ "$(call GET "/users/$uid" | jq -r '.activated')" = false ] || { echo "FAILED: $name is still activated" >&2; exit 1; }
  echo "deactivated $name"
done

echo "seeding finished"
